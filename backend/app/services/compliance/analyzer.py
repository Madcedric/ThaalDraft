from typing import Any, Dict, List, Optional
import time
from .schema import (
    ComplianceAnalysisResponse,
    ComplianceCheckType,
    ComplianceIssue,
    ComplianceReport,
    ComplianceScore,
    ComplianceStatus,
    ComplianceSeverity,
    JournalRule,
)
from .rules import get_journal_rule


def _count_words(text: str) -> int:
    return len(text.split()) if text else 0


def _check_word_count(
    word_count: int, rule: JournalRule
) -> Optional[ComplianceIssue]:
    if rule.min_words is None and rule.max_words is None:
        return None
    status = ComplianceStatus.PASS
    severity = ComplianceSeverity.INFO
    actual = str(word_count)
    expected_parts = []
    if rule.min_words is not None:
        expected_parts.append(f">= {rule.min_words}")
    if rule.max_words is not None:
        expected_parts.append(f"<= {rule.max_words}")
    expected = " and ".join(expected_parts)
    if rule.min_words is not None and word_count < rule.min_words:
        status = ComplianceStatus.FAIL
        severity = ComplianceSeverity.ERROR
    elif rule.max_words is not None and word_count > rule.max_words:
        status = ComplianceStatus.FAIL
        severity = ComplianceSeverity.ERROR
    return ComplianceIssue(
        check_type=ComplianceCheckType.WORD_COUNT,
        status=status,
        severity=severity,
        message=f"Word count is {word_count}",
        actual_value=actual,
        expected_value=expected,
        recommendation=(
            f"Adjust word count to be within {expected} words"
            if status == ComplianceStatus.FAIL
            else ""
        ),
    )


def _check_abstract_length(
    abstract: str, rule: JournalRule
) -> Optional[ComplianceIssue]:
    if rule.min_abstract_words is None and rule.max_abstract_words is None:
        return None
    word_count = _count_words(abstract)
    status = ComplianceStatus.PASS
    severity = ComplianceSeverity.INFO
    actual = str(word_count)
    expected_parts = []
    if rule.min_abstract_words is not None:
        expected_parts.append(f">= {rule.min_abstract_words}")
    if rule.max_abstract_words is not None:
        expected_parts.append(f"<= {rule.max_abstract_words}")
    expected = " and ".join(expected_parts)
    if not abstract or abstract.strip() == "":
        status = ComplianceStatus.FAIL
        severity = ComplianceSeverity.ERROR
        actual = "0 (missing)"
    elif rule.min_abstract_words is not None and word_count < rule.min_abstract_words:
        status = ComplianceStatus.WARN
        severity = ComplianceSeverity.WARNING
    elif rule.max_abstract_words is not None and word_count > rule.max_abstract_words:
        status = ComplianceStatus.WARN
        severity = ComplianceSeverity.WARNING
    return ComplianceIssue(
        check_type=ComplianceCheckType.ABSTRACT_LENGTH,
        status=status,
        severity=severity,
        message=f"Abstract length is {word_count} words",
        actual_value=actual,
        expected_value=expected,
        recommendation=(
            f"Adjust abstract to be within {expected} words"
            if status != ComplianceStatus.PASS
            else ""
        ),
    )


def _check_reference_count(
    ref_count: int, rule: JournalRule
) -> Optional[ComplianceIssue]:
    if rule.min_references is None:
        return None
    status = ComplianceStatus.PASS
    severity = ComplianceSeverity.INFO
    actual = str(ref_count)
    expected = f">= {rule.min_references}"
    if ref_count < rule.min_references:
        status = ComplianceStatus.FAIL
        severity = ComplianceSeverity.ERROR
    return ComplianceIssue(
        check_type=ComplianceCheckType.REFERENCE_COUNT,
        status=status,
        severity=severity,
        message=f"Reference count is {ref_count}",
        actual_value=actual,
        expected_value=expected,
        recommendation=(
            f"Add at least {rule.min_references - ref_count} more references"
            if status == ComplianceStatus.FAIL
            else ""
        ),
    )


def _check_citation_style(
    detected_style: str, rule: JournalRule
) -> Optional[ComplianceIssue]:
    if rule.citation_style == "unknown":
        return None
    status = ComplianceStatus.PASS
    severity = ComplianceSeverity.INFO
    actual = detected_style
    expected = rule.citation_style
    if detected_style.lower() != rule.citation_style.lower():
        status = ComplianceStatus.WARN
        severity = ComplianceSeverity.WARNING
    return ComplianceIssue(
        check_type=ComplianceCheckType.CITATION_STYLE,
        status=status,
        severity=severity,
        message=f"Citation style is '{detected_style}'",
        actual_value=actual,
        expected_value=expected,
        recommendation=(
            f"Convert citations to {rule.citation_style} style"
            if status == ComplianceStatus.WARN
            else ""
        ),
    )


def _check_figure_limit(
    figure_count: int, rule: JournalRule
) -> Optional[ComplianceIssue]:
    if rule.max_figures is None:
        return None
    status = ComplianceStatus.PASS
    severity = ComplianceSeverity.INFO
    actual = str(figure_count)
    expected = f"<= {rule.max_figures}"
    if figure_count > rule.max_figures:
        status = ComplianceStatus.WARN
        severity = ComplianceSeverity.WARNING
    return ComplianceIssue(
        check_type=ComplianceCheckType.FIGURE_LIMIT,
        status=status,
        severity=severity,
        message=f"Figure count is {figure_count}",
        actual_value=actual,
        expected_value=expected,
        recommendation=(
            f"Reduce figures to {rule.max_figures} or fewer"
            if status == ComplianceStatus.WARN
            else ""
        ),
    )


def _check_section_structure(
    sections: List[str], rule: JournalRule
) -> Optional[ComplianceIssue]:
    if not rule.required_sections:
        return None
    lower_sections = [s.lower().strip() for s in sections]
    missing = [
        req for req in rule.required_sections
        if not any(req.lower() in s for s in lower_sections)
    ]
    status = ComplianceStatus.PASS
    severity = ComplianceSeverity.INFO
    actual = f"{len(sections)} sections"
    expected = f"{len(rule.required_sections)} required"
    if missing:
        status = ComplianceStatus.WARN
        severity = ComplianceSeverity.WARNING
        actual = f"{len(sections)} sections (missing: {', '.join(missing)})"
    return ComplianceIssue(
        check_type=ComplianceCheckType.SECTION_STRUCTURE,
        status=status,
        severity=severity,
        message=f"Section structure check: {len(sections)} sections found",
        actual_value=actual,
        expected_value=expected,
        recommendation=(
            f"Add missing sections: {', '.join(missing)}"
            if missing
            else ""
        ),
    )


def _check_keyword_count(
    keyword_count: int, rule: JournalRule
) -> Optional[ComplianceIssue]:
    if rule.min_keywords is None and rule.max_keywords is None:
        return None
    status = ComplianceStatus.PASS
    severity = ComplianceSeverity.INFO
    actual = str(keyword_count)
    expected_parts = []
    if rule.min_keywords is not None:
        expected_parts.append(f">= {rule.min_keywords}")
    if rule.max_keywords is not None:
        expected_parts.append(f"<= {rule.max_keywords}")
    expected = " and ".join(expected_parts)
    if rule.min_keywords is not None and keyword_count < rule.min_keywords:
        status = ComplianceStatus.WARN
        severity = ComplianceSeverity.WARNING
    elif rule.max_keywords is not None and keyword_count > rule.max_keywords:
        status = ComplianceStatus.WARN
        severity = ComplianceSeverity.WARNING
    return ComplianceIssue(
        check_type=ComplianceCheckType.KEYWORD_COUNT,
        status=status,
        severity=severity,
        message=f"Keyword count is {keyword_count}",
        actual_value=actual,
        expected_value=expected,
        recommendation=(
            f"Adjust keywords to be within {expected}"
            if status != ComplianceStatus.PASS
            else ""
        ),
    )


def _check_title_length(
    title: str, rule: JournalRule
) -> Optional[ComplianceIssue]:
    if rule.title_max_words is None:
        return None
    word_count = _count_words(title)
    status = ComplianceStatus.PASS
    severity = ComplianceSeverity.INFO
    actual = str(word_count)
    expected = f"<= {rule.title_max_words}"
    if word_count > rule.title_max_words:
        status = ComplianceStatus.WARN
        severity = ComplianceSeverity.WARNING
    return ComplianceIssue(
        check_type=ComplianceCheckType.TITLE_LENGTH,
        status=status,
        severity=severity,
        message=f"Title length is {word_count} words",
        actual_value=actual,
        expected_value=expected,
        recommendation=(
            f"Shorten title to {rule.title_max_words} words or fewer"
            if status == ComplianceStatus.WARN
            else ""
        ),
    )


def _check_doi_required(
    has_doi: bool, rule: JournalRule
) -> Optional[ComplianceIssue]:
    if not rule.requires_doi:
        return None
    status = ComplianceStatus.PASS
    severity = ComplianceSeverity.INFO
    actual = "present" if has_doi else "missing"
    expected = "DOI required"
    if not has_doi:
        status = ComplianceStatus.FAIL
        severity = ComplianceSeverity.ERROR
    return ComplianceIssue(
        check_type=ComplianceCheckType.DOI_REQUIRED,
        status=status,
        severity=severity,
        message=f"DOI check: {actual}",
        actual_value=actual,
        expected_value=expected,
        recommendation="Add a DOI for this manuscript" if not has_doi else "",
    )


def _compute_score(
    issues: List[ComplianceIssue],
    checks_performed: int,
) -> ComplianceScore:
    if checks_performed == 0:
        return ComplianceScore(
            overall=100.0,
            word_count=100.0,
            abstract_length=100.0,
            reference_count=100.0,
            citation_style=100.0,
            figure_limit=100.0,
            section_structure=100.0,
            explanation="No checks performed",
        )

    check_scores: Dict[str, List[float]] = {}
    for issue in issues:
        check_type = issue.check_type.value
        if issue.status == ComplianceStatus.PASS:
            score = 100.0
        elif issue.status == ComplianceStatus.WARN:
            score = 70.0
        else:
            score = 0.0
        check_scores.setdefault(check_type, []).append(score)

    category_scores: Dict[str, float] = {}
    for check_type, scores in check_scores.items():
        category_scores[check_type] = sum(scores) / len(scores)

    all_scores = list(category_scores.values())
    overall = sum(all_scores) / len(all_scores) if all_scores else 100.0

    return ComplianceScore(
        overall=round(overall, 1),
        word_count=round(category_scores.get("word_count", 100.0), 1),
        abstract_length=round(category_scores.get("abstract_length", 100.0), 1),
        reference_count=round(category_scores.get("reference_count", 100.0), 1),
        citation_style=round(category_scores.get("citation_style", 100.0), 1),
        figure_limit=round(category_scores.get("figure_limit", 100.0), 1),
        section_structure=round(category_scores.get("section_structure", 100.0), 1),
        explanation=f"Overall compliance: {overall:.1f}%",
    )


def analyze_compliance(
    document_id: str,
    journal_id: str,
    structured_data: Dict[str, Any],
    citation_report: Optional[Dict[str, Any]] = None,
) -> ComplianceReport:
    start_time = time.time()

    rule = get_journal_rule(journal_id)
    if rule is None:
        rule = get_journal_rule("custom")

    title = structured_data.get("title", "")
    abstract = structured_data.get("abstract", "")
    sections = structured_data.get("sections", [])
    references = structured_data.get("references", [])
    keywords = structured_data.get("keywords", [])
    authors = structured_data.get("authors", [])
    metadata = structured_data.get("metadata", {})
    figures = structured_data.get("figures", [])
    doi = metadata.get("doi", "")

    word_count = metadata.get("word_count", 0)
    if word_count == 0:
        all_text = " ".join(
            s.get("content", "") for s in sections if isinstance(s, dict)
        )
        word_count = _count_words(all_text)

    section_headings = [
        s.get("heading", "") for s in sections if isinstance(s, dict)
    ]

    detected_style = "unknown"
    if citation_report:
        detected_style = citation_report.get("citation_style", "unknown")

    figure_count = len(figures) if isinstance(figures, list) else 0

    issues: List[ComplianceIssue] = []

    word_issue = _check_word_count(word_count, rule)
    if word_issue:
        issues.append(word_issue)

    abstract_issue = _check_abstract_length(abstract, rule)
    if abstract_issue:
        issues.append(abstract_issue)

    ref_count = len(references) if isinstance(references, list) else 0
    ref_issue = _check_reference_count(ref_count, rule)
    if ref_issue:
        issues.append(ref_issue)

    citation_issue = _check_citation_style(detected_style, rule)
    if citation_issue:
        issues.append(citation_issue)

    figure_issue = _check_figure_limit(figure_count, rule)
    if figure_issue:
        issues.append(figure_issue)

    section_issue = _check_section_structure(section_headings, rule)
    if section_issue:
        issues.append(section_issue)

    keyword_issue = _check_keyword_count(len(keywords), rule)
    if keyword_issue:
        issues.append(keyword_issue)

    title_issue = _check_title_length(title, rule)
    if title_issue:
        issues.append(title_issue)

    doi_issue = _check_doi_required(bool(doi), rule)
    if doi_issue:
        issues.append(doi_issue)

    checks_performed = len(issues)
    checks_passed = sum(1 for i in issues if i.status == ComplianceStatus.PASS)
    checks_failed = sum(1 for i in issues if i.status == ComplianceStatus.FAIL)
    checks_warned = sum(1 for i in issues if i.status == ComplianceStatus.WARN)

    score = _compute_score(issues, checks_performed)

    processing_time_ms = (time.time() - start_time) * 1000

    return ComplianceReport(
        document_id=document_id,
        journal_id=rule.journal_id,
        journal_name=rule.journal_name,
        score=score,
        issues=issues,
        checks_performed=checks_performed,
        checks_passed=checks_passed,
        checks_failed=checks_failed,
        checks_warned=checks_warned,
        processing_metadata={
            "processing_time_ms": round(processing_time_ms, 2),
            "journal_rule_applied": rule.journal_id,
        },
    )
