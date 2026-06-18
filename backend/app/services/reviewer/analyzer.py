from typing import Any, Dict, List, Optional
import time
import re
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
    sentence_count = _count_sentences(all_content)

    score = 100.0
    findings_count = 0

    if word_count < 1000:
        score -= 20
        findings_count += 1
    if avg_sent_len > 30:
        score -= 15
        findings_count += 1
    if avg_sent_len < 5 and avg_sent_len > 0:
        score -= 10
        findings_count += 1

    abstract = _get_section_content(sections, "abstract")
    if not abstract or len(abstract.split()) < 50:
        score -= 10
        findings_count += 1

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
        score -= len(missing) * 15
        findings_count += len(missing)

    intro = _get_section_content(sections, "introduction")
    if intro and "objective" not in intro.lower() and "goal" not in intro.lower() and "aim" not in intro.lower():
        score -= 10
        findings_count += 1

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
        score = 30.0
        findings_count = 1
    else:
        word_count = len(methodology_content.split())
        if word_count < 200:
            score -= 30
            findings_count += 1
        methodology_keywords = ["method", "approach", "dataset", "experiment", "evaluation", "algorithm"]
        present = sum(1 for k in methodology_keywords if k in methodology_content.lower())
        if present < 2:
            score -= 20
            findings_count += 1

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
        score -= 30
        findings_count += 1
    elif ref_count < 20:
        score -= 15
        findings_count += 1

    if citation_report:
        unresolved = citation_report.get("unresolved_citations", 0)
        if unresolved > 0:
            score -= min(20, unresolved * 5)
            findings_count += 1

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
        score = 20.0
        findings_count = 1
    elif ref_count == 0:
        score = 30.0
        findings_count = 1
    else:
        ratio = citation_count / max(ref_count, 1)
        if ratio < 0.5:
            score -= 30
            findings_count += 1
        elif ratio < 1.0:
            score -= 10
            findings_count += 1

    if citation_report:
        health = citation_report.get("health_score", {})
        overall_health = health.get("overall", 100)
        if overall_health < 70:
            score = min(score, overall_health)
            findings_count += 1

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
        score -= 20
        findings_count += 1
    if not limitations:
        score -= 15
        findings_count += 1

    score = max(0.0, min(100.0, score))
    return CategoryScore(
        category=ReviewCategory.RESEARCH_GAPS,
        score=round(score, 1),
        summary=f"Future work: {'present' if future_work else 'missing'}, limitations: {'present' if limitations else 'missing'}",
        finding_count=findings_count,
    )


def _compute_publication_readiness(category_scores: List[CategoryScore]) -> PublicationReadiness:
    if not category_scores:
        return PublicationReadiness(overall=0.0, label="Not Ready", summary="No analysis performed")

    overall = sum(c.score for c in category_scores) / len(category_scores)

    if overall >= 85:
        label = "Ready"
        summary = "Manuscript meets most quality standards"
    elif overall >= 70:
        label = "Conditionally Ready"
        summary = "Minor revisions recommended before submission"
    elif overall >= 50:
        label = "Needs Revision"
        summary = "Significant revisions required"
    else:
        label = "Not Ready"
        summary = "Major rewrites needed"

    return PublicationReadiness(
        overall=round(overall, 1),
        label=label,
        summary=summary,
    )


def _generate_strengths(
    category_scores: List[CategoryScore],
    structured_data: Dict,
) -> List[ReviewStrength]:
    strengths = []
    sections = structured_data.get("sections", [])

    for cs in category_scores:
        if cs.score >= 80:
            strengths.append(ReviewStrength(
                category=cs.category,
                title=f"Strong {cs.category.value.replace('_', ' ')}",
                description=cs.summary,
            ))

    ref_count = len(structured_data.get("references", [])) if isinstance(structured_data.get("references"), list) else 0
    if ref_count >= 20:
        strengths.append(ReviewStrength(
            category=ReviewCategory.LITERATURE_COVERAGE,
            title="Comprehensive Reference List",
            description=f"Manuscript includes {ref_count} references",
        ))

    abstract = ""
    for s in sections:
        if isinstance(s, dict) and s.get("label", "").lower() == "abstract":
            abstract = s.get("content", "")
            break
    if abstract and 100 <= len(abstract.split()) <= 300:
        strengths.append(ReviewStrength(
            category=ReviewCategory.WRITING_QUALITY,
            title="Well-structured Abstract",
            description=f"Abstract is {len(abstract.split())} words, within optimal range",
        ))

    return strengths


def _generate_weaknesses(
    category_scores: List[CategoryScore],
    structured_data: Dict,
    citation_report: Optional[Dict],
) -> List[ReviewFinding]:
    weaknesses = []
    sections = structured_data.get("sections", [])

    for cs in category_scores:
        if cs.score < 60:
            weaknesses.append(ReviewFinding(
                category=cs.category,
                severity=ReviewSeverity.CRITICAL if cs.score < 40 else ReviewSeverity.MAJOR,
                title=f"Weak {cs.category.value.replace('_', ' ')}",
                description=cs.summary,
                recommendation=f"Improve {cs.category.value.replace('_', ' ')} section",
            ))

    abstract = ""
    for s in sections:
        if isinstance(s, dict) and s.get("label", "").lower() == "abstract":
            abstract = s.get("content", "")
            break
    if not abstract or len(abstract.split()) < 50:
        weaknesses.append(ReviewFinding(
            category=ReviewCategory.WRITING_QUALITY,
            severity=ReviewSeverity.MAJOR,
            title="Missing or Insufficient Abstract",
            description="Abstract is missing or too short",
            recommendation="Write a 100-300 word abstract summarizing the research",
        ))

    methodology = ""
    for s in sections:
        if isinstance(s, dict) and s.get("label", "").lower() == "methodology":
            methodology = s.get("content", "")
            break
    if not methodology:
        weaknesses.append(ReviewFinding(
            category=ReviewCategory.METHODOLOGY,
            severity=ReviewSeverity.CRITICAL,
            title="Missing Methodology Section",
            description="No methodology section found",
            recommendation="Add a detailed methodology section describing your approach",
        ))

    if citation_report:
        health = citation_report.get("health_score", {})
        if health.get("overall", 100) < 70:
            weaknesses.append(ReviewFinding(
                category=ReviewCategory.CITATION_COMPLETENESS,
                severity=ReviewSeverity.MAJOR,
                title="Citation Health Issues",
                description=f"Citation health score is {health.get('overall', 0)}/100",
                recommendation="Review and fix citation issues before submission",
            ))

    return weaknesses


def _generate_improvement_suggestions(
    category_scores: List[CategoryScore],
    structured_data: Dict,
) -> List[str]:
    suggestions = []

    for cs in category_scores:
        if cs.score < 70:
            suggestions.append(
                f"Improve {cs.category.value.replace('_', ' ')}: {cs.summary}"
            )

    sections = structured_data.get("sections", [])
    section_labels = [s.get("label", "").lower() for s in sections if isinstance(s, dict)]

    if "discussion" not in section_labels:
        suggestions.append("Add a Discussion section to interpret your results")
    if "future work" not in " ".join(section_labels):
        suggestions.append("Include a Future Work section to outline next steps")

    references = structured_data.get("references", [])
    ref_count = len(references) if isinstance(references, list) else 0
    if ref_count < 15:
        suggestions.append(f"Increase reference count (currently {ref_count}, aim for 15+)")

    return suggestions


def analyze_review(
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

    strengths = _generate_strengths(category_scores, structured_data)
    weaknesses = _generate_weaknesses(category_scores, structured_data, citation_report)
    suggestions = _generate_improvement_suggestions(category_scores, structured_data)

    references = structured_data.get("references", [])
    citations = structured_data.get("citations", [])
    ref_texts = [r.get("raw_text", "") for r in references if isinstance(r, dict)] if isinstance(references, list) else []
    cit_texts = [c for c in citations if isinstance(c, str)] if isinstance(citations, list) else []

    missing_refs = []
    for cit in cit_texts:
        found = False
        for ref in ref_texts:
            if cit[:20].lower() in ref.lower():
                found = True
                break
        if not found and cit:
            missing_refs.append(cit[:100])

    critical_count = sum(1 for w in weaknesses if w.severity == ReviewSeverity.CRITICAL)
    major_count = sum(1 for w in weaknesses if w.severity == ReviewSeverity.MAJOR)
    minor_count = sum(1 for w in weaknesses if w.severity == ReviewSeverity.MINOR)
    suggestion_count = len(suggestions)

    publication_readiness = _compute_publication_readiness(category_scores)

    processing_time_ms = (time.time() - start_time) * 1000

    return ReviewReport(
        document_id=document_id,
        journal_id=journal_id,
        strengths=strengths,
        weaknesses=weaknesses,
        missing_references=missing_refs[:10],
        improvement_suggestions=suggestions,
        category_scores=category_scores,
        publication_readiness=publication_readiness,
        total_findings=len(weaknesses),
        critical_count=critical_count,
        major_count=major_count,
        minor_count=minor_count,
        suggestion_count=suggestion_count,
        analysis_method="deterministic",
        processing_metadata={
            "processing_time_ms": round(processing_time_ms, 2),
            "sections_analyzed": len(structured_data.get("sections", [])),
            "references_count": len(references) if isinstance(references, list) else 0,
        },
    )
