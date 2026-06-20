"""AI Reviewer Engine — v2.

Uses Ollama (qwen3:4b) for manuscript review with deterministic fallback.
"""
import time
import logging
from typing import Any, Dict, List, Optional

from app.services.ollama_service import is_available as ollama_available, chat as ollama_chat, extract_json
from app.services.manuscript.model import StructuredManuscript

logger = logging.getLogger(__name__)


REVIEW_SYSTEM_PROMPT = """You are an expert academic peer reviewer. Analyze the manuscript and provide a structured review.

You MUST respond with valid JSON in the following format:
{
  "strengths": [
    {"category": "writing_quality|research_clarity|methodology|literature_coverage|citation_completeness|research_gaps", "title": "Brief title", "description": "Detailed description"}
  ],
  "weaknesses": [
    {"category": "writing_quality|research_clarity|methodology|literature_coverage|citation_completeness|research_gaps", "severity": "critical|major|minor|suggestion", "title": "Brief title", "description": "Detailed description", "recommendation": "Actionable recommendation"}
  ],
  "improvement_suggestions": ["suggestion 1", "suggestion 2"],
  "category_scores": {
    "writing_quality": 0-100,
    "research_clarity": 0-100,
    "methodology": 0-100,
    "literature_coverage": 0-100,
    "citation_completeness": 0-100,
    "research_gaps": 0-100
  },
  "publication_readiness": {
    "overall": 0-100,
    "label": "Ready|Conditionally Ready|Needs Revision|Not Ready",
    "summary": "Brief assessment"
  }
}

Be thorough, specific, and constructive. Focus on academic quality, not formatting."""


def _manuscript_to_text(manuscript: StructuredManuscript) -> str:
    """Convert manuscript to text for LLM review."""
    parts = [f"Title: {manuscript.title}"]

    if manuscript.authors:
        names = ", ".join(a.name for a in manuscript.authors)
        parts.append(f"Authors: {names}")

    if manuscript.abstract:
        parts.append(f"Abstract: {manuscript.abstract}")

    for sec in manuscript.sections:
        if sec.content and sec.label.value not in ("title", "abstract", "keywords", "references"):
            parts.append(f"\n## {sec.heading}\n{sec.content}")

    if manuscript.references:
        parts.append("\nReferences:")
        for ref in manuscript.references[:30]:
            parts.append(f"[{ref.index}] {ref.raw_text}")

    text = "\n".join(parts)
    if len(text) > 8000:
        text = text[:8000] + "\n\n[Truncated due to length]"
    return text


def llm_review(manuscript: StructuredManuscript, journal_id: Optional[str] = None) -> Optional[Dict]:
    """Call Ollama for a structured review. Returns parsed JSON or None."""
    if not ollama_available():
        logger.warning("Ollama not available, cannot run LLM review")
        return None

    context = f"Target journal: {journal_id}\n" if journal_id else ""
    manuscript_text = _manuscript_to_text(manuscript)

    prompt = f"""Review this academic manuscript. Provide thorough, specific feedback.

{context}{manuscript_text}

Respond with the required JSON format. Be specific about issues found in the text."""

    logger.info("Calling Ollama for manuscript review...")
    start = time.time()
    response_text = ollama_chat(prompt, system=REVIEW_SYSTEM_PROMPT)
    elapsed = time.time() - start
    logger.info(f"Ollama review completed in {elapsed:.1f}s")

    if not response_text:
        return None

    return extract_json(response_text)


def deterministic_review(manuscript: StructuredManuscript) -> Dict:
    """Fast deterministic review without LLM."""
    category_scores = {}

    # Writing quality
    total_words = manuscript.word_count
    avg_section_length = total_words / max(manuscript.section_count, 1)
    wq_score = 100.0
    if total_words < 1000:
        wq_score -= 20
    if avg_section_length > 500:
        wq_score -= 10
    category_scores["writing_quality"] = max(0, min(100, wq_score))

    # Research clarity
    required = ["introduction", "methodology", "methods", "results", "conclusion"]
    detected = {s.label.value for s in manuscript.sections}
    missing = [r for r in required if not any(r in d for d in detected)]
    rc_score = max(0, 100 - len(missing) * 15)
    category_scores["research_clarity"] = rc_score

    # Methodology
    has_method = any(
        s.label.value in ("methodology", "methods", "experiments")
        for s in manuscript.sections
    )
    category_scores["methodology"] = 80 if has_method else 30

    # Literature coverage
    ref_count = manuscript.reference_count
    lc_score = 100
    if ref_count < 10:
        lc_score = 50
    elif ref_count < 20:
        lc_score = 70
    category_scores["literature_coverage"] = lc_score

    # Citation completeness
    has_refs = manuscript.reference_count > 0
    category_scores["citation_completeness"] = 80 if has_refs else 20

    # Research gaps
    all_content = " ".join(s.content.lower() for s in manuscript.sections)
    has_future = "future work" in all_content
    has_limitations = "limitation" in all_content
    rg_score = 100
    if not has_future:
        rg_score -= 20
    if not has_limitations:
        rg_score -= 15
    category_scores["research_gaps"] = max(0, rg_score)

    overall = sum(category_scores.values()) / len(category_scores)

    if overall >= 85:
        label, summary = "Ready", "Manuscript meets most quality standards"
    elif overall >= 70:
        label, summary = "Conditionally Ready", "Minor revisions recommended"
    elif overall >= 50:
        label, summary = "Needs Revision", "Significant revisions required"
    else:
        label, summary = "Not Ready", "Major rewrites needed"

    strengths = []
    weaknesses = []
    for cat, score in category_scores.items():
        if score >= 80:
            strengths.append({"category": cat, "title": f"Strong {cat.replace('_', ' ')}", "description": f"Score: {score}/100"})
        if score < 60:
            weaknesses.append({
                "category": cat,
                "severity": "critical" if score < 40 else "major",
                "title": f"Weak {cat.replace('_', ' ')}",
                "description": f"Score: {score}/100",
                "recommendation": f"Improve {cat.replace('_', ' ')}",
            })

    return {
        "strengths": strengths,
        "weaknesses": weaknesses,
        "improvement_suggestions": [f"Improve {cat}: score is {score}/100" for cat, score in category_scores.items() if score < 70],
        "category_scores": category_scores,
        "publication_readiness": {
            "overall": round(overall, 1),
            "label": label,
            "summary": summary,
        },
        "analysis_method": "deterministic",
    }


def review_manuscript(
    manuscript: StructuredManuscript,
    journal_id: Optional[str] = None,
) -> Dict:
    """Review a manuscript. Tries Ollama first, falls back to deterministic."""
    if ollama_available():
        logger.info("Using Ollama LLM for review")
        llm_result = llm_review(manuscript, journal_id)
        if llm_result:
            llm_result["analysis_method"] = "llm (ollama)"
            return llm_result
        logger.warning("LLM review failed, falling back to deterministic")

    logger.info("Using deterministic review")
    return deterministic_review(manuscript)
