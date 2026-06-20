import os
import json
import time
import logging
import re
from typing import Any, Dict, List, Optional

from app.services.ollama_service import (
    is_available as ollama_available,
    chat as ollama_chat,
    extract_json as ollama_extract_json,
    OLLAMA_MODEL,
)

from .schema import (
    ReviewAnalysisResponse,
    ReviewCategory,
    ReviewFinding,
    ReviewReport,
    ReviewSeverity,
    ReviewStrength,
    CategoryScore,
    PublicationReadiness,
)

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


def _llm_review(
    structured_data: Dict[str, Any],
    citation_report: Optional[Dict[str, Any]] = None,
    journal_id: Optional[str] = None,
) -> Optional[Dict]:
    sections = structured_data.get("sections", [])
    title = structured_data.get("title", "Untitled")
    abstract = structured_data.get("abstract", "")
    authors = structured_data.get("authors", [])
    references = structured_data.get("references", [])

    manuscript_text = f"Title: {title}\n\n"
    if authors:
        if isinstance(authors[0], dict):
            manuscript_text += "Authors: " + ", ".join(a.get("name", str(a)) for a in authors) + "\n\n"
        else:
            manuscript_text += "Authors: " + ", ".join(str(a) for a in authors) + "\n\n"
    if abstract:
        manuscript_text += f"Abstract: {abstract}\n\n"
    for s in sections:
        if isinstance(s, dict):
            heading = s.get("heading", "")
            content = s.get("content", "")
            if heading and content:
                manuscript_text += f"## {heading}\n{content}\n\n"
    if references:
        manuscript_text += "References:\n"
        for i, ref in enumerate(references[:30]):
            if isinstance(ref, dict):
                manuscript_text += f"[{i+1}] {ref.get('raw_text', str(ref))}\n"
            else:
                manuscript_text += f"[{i+1}] {str(ref)}\n"

    if len(manuscript_text) > 12000:
        manuscript_text = manuscript_text[:12000] + "\n\n[Truncated due to length]"

    context = f"Target journal: {journal_id or 'general'}\n" if journal_id else ""
    if citation_report:
        health = citation_report.get("health_score", {})
        context += f"Citation health score: {health.get('overall', 'unknown')}%\n"
        context += f"Total citations: {citation_report.get('total_citations', 0)}\n"
        context += f"Total references: {citation_report.get('total_references', 0)}\n"

    prompt = f"""Review this academic manuscript. Provide thorough, specific feedback.

{context}
{manuscript_text}

Respond with the required JSON format. Be specific about issues found in the text."""

    response_text = ollama_chat(prompt, system=REVIEW_SYSTEM_PROMPT)
    if not response_text:
        return None

    return ollama_extract_json(response_text)


def _get_section_content(sections: List[Dict], label: str) -> str:
    for s in sections:
        if isinstance(s, dict) and s.get("label", "").lower() == label.lower():
            return s.get("content", "")
    return ""


def _count_sentences(text: str) -> int:
    return len(re.split(r'[.!?]+', text.strip())) if text else 0


def _avg_sentence_length(text: str) -> float:
    sentences = [s.strip() for s in re.split(r'[.!?]+', text.strip()) if s.strip()]
    if not sentences:
        return 0.0
    return sum(len(s.split()) for s in sentences) / len(sentences)


def _check_writing_quality(structured_data: Dict) -> CategoryScore:
    sections = structured_data.get("sections", [])
    all_content = " ".join(s.get("content", "") for s in sections if isinstance(s, dict))
    word_count = len(all_content.split())
    avg_sent_len = _avg_sentence_length(all_content)

    score = 100.0
    findings_count = 0
    if word_count < 1000:
        score -= 20; findings_count += 1
    if avg_sent_len > 30:
        score -= 15; findings_count += 1
    abstract = _get_section_content(sections, "abstract")
    if not abstract or len(abstract.split()) < 50:
        score -= 10; findings_count += 1
    score = max(0.0, min(100.0, score))
    return CategoryScore(
        category=ReviewCategory.WRITING_QUALITY,
        score=round(score, 1),
        summary=f"Word count: {word_count}, avg sentence length: {avg_sent_len:.1f} words",
        finding_count=findings_count,
    )


def _check_research_clarity(structured_data: Dict) -> CategoryScore:
    sections = structured_data.get("sections", [])
    section_labels = [s.get("label", "").lower() for s in sections if isinstance(s, dict)]
    required = ["introduction", "methodology", "results", "conclusion"]
    missing = [r for r in required if not any(r in label for label in section_labels)]
    score = 100.0
    findings_count = 0
    if missing:
        score -= len(missing) * 15; findings_count += len(missing)
    score = max(0.0, min(100.0, score))
    return CategoryScore(
        category=ReviewCategory.RESEARCH_CLARITY,
        score=round(score, 1),
        summary=f"Sections present: {len(sections)}, missing: {len(missing)}",
        finding_count=findings_count,
    )


def _check_methodology(structured_data: Dict) -> CategoryScore:
    sections = structured_data.get("sections", [])
    methodology_content = _get_section_content(sections, "methodology")
    score = 100.0
    findings_count = 0
    if not methodology_content:
        score = 30.0; findings_count = 1
    else:
        if len(methodology_content.split()) < 200:
            score -= 30; findings_count += 1
    score = max(0.0, min(100.0, score))
    return CategoryScore(
        category=ReviewCategory.METHODOLOGY,
        score=round(score, 1),
        summary=f"Methodology section: {'present' if methodology_content else 'missing'}",
        finding_count=findings_count,
    )


def _check_literature_coverage(structured_data: Dict, citation_report: Optional[Dict]) -> CategoryScore:
    references = structured_data.get("references", [])
    ref_count = len(references) if isinstance(references, list) else 0
    score = 100.0
    findings_count = 0
    if ref_count < 10:
        score -= 30; findings_count += 1
    elif ref_count < 20:
        score -= 15; findings_count += 1
    if citation_report:
        unresolved = citation_report.get("unresolved_citations", 0)
        if unresolved > 0:
            score -= min(20, unresolved * 5); findings_count += 1
    score = max(0.0, min(100.0, score))
    return CategoryScore(
        category=ReviewCategory.LITERATURE_COVERAGE,
        score=round(score, 1),
        summary=f"References: {ref_count}",
        finding_count=findings_count,
    )


def _check_citation_completeness(structured_data: Dict, citation_report: Optional[Dict]) -> CategoryScore:
    citations = structured_data.get("citations", [])
    references = structured_data.get("references", [])
    citation_count = len(citations) if isinstance(citations, list) else 0
    ref_count = len(references) if isinstance(references, list) else 0
    score = 100.0
    findings_count = 0
    if citation_count == 0:
        score = 20.0; findings_count = 1
    elif ref_count == 0:
        score = 30.0; findings_count = 1
    else:
        ratio = citation_count / max(ref_count, 1)
        if ratio < 0.5:
            score -= 30; findings_count += 1
    score = max(0.0, min(100.0, score))
    return CategoryScore(
        category=ReviewCategory.CITATION_COMPLETENESS,
        score=round(score, 1),
        summary=f"Citations: {citation_count}, references: {ref_count}",
        finding_count=findings_count,
    )


def _check_research_gaps(structured_data: Dict) -> CategoryScore:
    sections = structured_data.get("sections", [])
    future_work = False
    limitations = False
    for s in sections:
        if isinstance(s, dict):
            heading = s.get("heading", "").lower()
            content = s.get("content", "").lower()
            if "future work" in heading or "future work" in content[:200]:
                future_work = True
            if "limitation" in heading or "limitation" in content[:200]:
                limitations = True
    score = 100.0
    findings_count = 0
    if not future_work:
        score -= 20; findings_count += 1
    if not limitations:
        score -= 15; findings_count += 1
    score = max(0.0, min(100.0, score))
    return CategoryScore(
        category=ReviewCategory.RESEARCH_GAPS,
        score=round(score, 1),
        summary=f"Future work: {'present' if future_work else 'missing'}, limitations: {'present' if limitations else 'missing'}",
        finding_count=findings_count,
    )


def _deterministic_review(
    document_id: str,
    structured_data: Dict[str, Any],
    citation_report: Optional[Dict[str, Any]] = None,
    journal_id: Optional[str] = None,
) -> ReviewReport:
    start_time = time.time()
    category_scores = [
        _check_writing_quality(structured_data),
        _check_research_clarity(structured_data),
        _check_methodology(structured_data),
        _check_literature_coverage(structured_data, citation_report),
        _check_citation_completeness(structured_data, citation_report),
        _check_research_gaps(structured_data),
    ]

    strengths = []
    for cs in category_scores:
        if cs.score >= 80:
            strengths.append(ReviewStrength(
                category=cs.category,
                title=f"Strong {cs.category.value.replace('_', ' ')}",
                description=cs.summary,
            ))

    weaknesses = []
    for cs in category_scores:
        if cs.score < 60:
            weaknesses.append(ReviewFinding(
                category=cs.category,
                severity=ReviewSeverity.CRITICAL if cs.score < 40 else ReviewSeverity.MAJOR,
                title=f"Weak {cs.category.value.replace('_', ' ')}",
                description=cs.summary,
                recommendation=f"Improve {cs.category.value.replace('_', ' ')} section",
            ))

    suggestions = []
    for cs in category_scores:
        if cs.score < 70:
            suggestions.append(f"Improve {cs.category.value.replace('_', ' ')}: {cs.summary}")

    overall = sum(c.score for c in category_scores) / len(category_scores) if category_scores else 0
    if overall >= 85:
        label, summary = "Ready", "Manuscript meets most quality standards"
    elif overall >= 70:
        label, summary = "Conditionally Ready", "Minor revisions recommended"
    elif overall >= 50:
        label, summary = "Needs Revision", "Significant revisions required"
    else:
        label, summary = "Not Ready", "Major rewrites needed"

    processing_time_ms = (time.time() - start_time) * 1000

    return ReviewReport(
        document_id=document_id,
        journal_id=journal_id,
        strengths=strengths,
        weaknesses=weaknesses,
        missing_references=[],
        improvement_suggestions=suggestions,
        category_scores=category_scores,
        publication_readiness=PublicationReadiness(overall=round(overall, 1), label=label, summary=summary),
        total_findings=len(weaknesses),
        critical_count=sum(1 for w in weaknesses if w.severity == ReviewSeverity.CRITICAL),
        major_count=sum(1 for w in weaknesses if w.severity == ReviewSeverity.MAJOR),
        minor_count=sum(1 for w in weaknesses if w.severity == ReviewSeverity.MINOR),
        suggestion_count=len(suggestions),
        analysis_method="deterministic",
        processing_metadata={
            "processing_time_ms": round(processing_time_ms, 2),
            "sections_analyzed": len(structured_data.get("sections", [])),
            "references_count": len(structured_data.get("references", [])),
        },
    )


def _llm_based_review(
    document_id: str,
    structured_data: Dict[str, Any],
    citation_report: Optional[Dict[str, Any]] = None,
    journal_id: Optional[str] = None,
) -> Optional[ReviewReport]:
    start_time = time.time()

    llm_result = _llm_review(structured_data, citation_report, journal_id)
    if not llm_result:
        return None

    try:
        category_scores = []
        cs_data = llm_result.get("category_scores", {})
        for cat_name, score_val in cs_data.items():
            try:
                cat = ReviewCategory(cat_name)
                category_scores.append(CategoryScore(
                    category=cat,
                    score=float(score_val),
                    summary=f"LLM assessment: {cat_name}",
                    finding_count=0,
                ))
            except (ValueError, TypeError):
                continue

        if not category_scores:
            category_scores = [
                _check_writing_quality(structured_data),
                _check_research_clarity(structured_data),
                _check_methodology(structured_data),
                _check_literature_coverage(structured_data, citation_report),
                _check_citation_completeness(structured_data, citation_report),
                _check_research_gaps(structured_data),
            ]

        strengths = []
        for s in llm_result.get("strengths", []):
            try:
                cat = ReviewCategory(s.get("category", "writing_quality"))
                strengths.append(ReviewStrength(
                    category=cat,
                    title=s.get("title", "Strength"),
                    description=s.get("description", ""),
                ))
            except (ValueError, TypeError):
                continue

        weaknesses = []
        for w in llm_result.get("weaknesses", []):
            try:
                cat = ReviewCategory(w.get("category", "writing_quality"))
                sev_str = w.get("severity", "minor")
                sev = ReviewSeverity(sev_str) if sev_str in [s.value for s in ReviewSeverity] else ReviewSeverity.MINOR
                weaknesses.append(ReviewFinding(
                    category=cat,
                    severity=sev,
                    title=w.get("title", "Issue"),
                    description=w.get("description", ""),
                    recommendation=w.get("recommendation"),
                ))
            except (ValueError, TypeError):
                continue

        suggestions = llm_result.get("improvement_suggestions", [])

        pr_data = llm_result.get("publication_readiness", {})
        pr_overall = float(pr_data.get("overall", 50))
        pr_label = pr_data.get("label", "Needs Revision")
        pr_summary = pr_data.get("summary", "LLM-based assessment")

        if not strengths:
            for cs in category_scores:
                if cs.score >= 80:
                    strengths.append(ReviewStrength(
                        category=cs.category,
                        title=f"Strong {cs.category.value.replace('_', ' ')}",
                        description=cs.summary,
                    ))

        if not weaknesses:
            for cs in category_scores:
                if cs.score < 60:
                    weaknesses.append(ReviewFinding(
                        category=cs.category,
                        severity=ReviewSeverity.MAJOR,
                        title=f"Weak {cs.category.value.replace('_', ' ')}",
                        description=cs.summary,
                        recommendation=f"Improve {cs.category.value.replace('_', ' ')}",
                    ))

        if not suggestions:
            for cs in category_scores:
                if cs.score < 70:
                    suggestions.append(f"Improve {cs.category.value.replace('_', ' ')}: {cs.summary}")

        processing_time_ms = (time.time() - start_time) * 1000

        return ReviewReport(
            document_id=document_id,
            journal_id=journal_id,
            strengths=strengths,
            weaknesses=weaknesses,
            missing_references=[],
            improvement_suggestions=suggestions,
            category_scores=category_scores,
            publication_readiness=PublicationReadiness(
                overall=round(pr_overall, 1),
                label=pr_label,
                summary=pr_summary,
            ),
            total_findings=len(weaknesses),
            critical_count=sum(1 for w in weaknesses if w.severity == ReviewSeverity.CRITICAL),
            major_count=sum(1 for w in weaknesses if w.severity == ReviewSeverity.MAJOR),
            minor_count=sum(1 for w in weaknesses if w.severity == ReviewSeverity.MINOR),
            suggestion_count=len(suggestions),
            analysis_method=f"llm ({OLLAMA_MODEL})",
            processing_metadata={
                "processing_time_ms": round(processing_time_ms, 2),
                "sections_analyzed": len(structured_data.get("sections", [])),
                "references_count": len(structured_data.get("references", [])),
                "model": OLLAMA_MODEL,
            },
        )
    except Exception as e:
        logger.warning(f"Failed to parse LLM review response: {e}")
        return None


def analyze_review(
    document_id: str,
    structured_data: Dict[str, Any],
    citation_report: Optional[Dict[str, Any]] = None,
    journal_id: Optional[str] = None,
) -> ReviewReport:
    if ollama_available():
        logger.info("Using Ollama LLM for review analysis")
        llm_report = _llm_based_review(document_id, structured_data, citation_report, journal_id)
        if llm_report:
            return llm_report
        logger.warning("LLM review failed, falling back to deterministic")

    logger.info("Using deterministic review analysis")
    return _deterministic_review(document_id, structured_data, citation_report, journal_id)
