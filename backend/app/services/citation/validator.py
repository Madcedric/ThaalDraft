import re
from typing import List, Dict, Any, Optional, Tuple

from app.services.citation.schema import (
    Citation,
    ReferenceValidation,
    CitationIssue,
    CitationIssueType,
    CitationSeverity,
    CitationHealthScore,
)
from app.services.citation.extractor import extract_dois_from_references


def _normalize_text(text: str) -> str:
    text = re.sub(r"[^\w\s]", "", text.lower())
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _fuzzy_match(text1: str, text2: str) -> float:
    norm1 = _normalize_text(text1)
    norm2 = _normalize_text(text2)

    if not norm1 or not norm2:
        return 0.0

    words1 = set(norm1.split())
    words2 = set(norm2.split())

    intersection = words1 & words2
    union = words1 | words2

    if not union:
        return 0.0

    return len(intersection) / len(union)


def _match_citation_to_reference(
    citation: Citation,
    references: List[Dict[str, Any]],
) -> Tuple[int, float]:
    if citation.type.value == "numeric":
        numbers = re.findall(r"\d+", citation.raw_text)
        for num_str in numbers:
            try:
                idx = int(num_str) - 1
                if 0 <= idx < len(references):
                    return idx, 1.0
            except ValueError:
                continue

    if citation.type.value == "author_year":
        author, year = _extract_author_year(citation.raw_text)
        if author and year:
            best_idx = -1
            best_score = 0.0
            for i, ref in enumerate(references):
                raw_text = ref.get("raw_text", "") if isinstance(ref, dict) else str(ref)
                ref_lower = raw_text.lower()
                author_lower = author.lower()
                if author_lower in ref_lower and str(year) in ref_lower:
                    score = 0.9
                    if best_score < score:
                        best_score = score
                        best_idx = i
            if best_idx >= 0:
                return best_idx, best_score

    return -1, 0.0


def _extract_author_year(text: str) -> Tuple[Optional[str], Optional[int]]:
    text = re.sub(r"[\(\)\[\]]", "", text)

    match = re.match(
        r"([A-Z][a-z]+(?:\s+et\s+al\.?)?)(?:,\s*)?(\d{4})?",
        text,
    )
    if match:
        author = match.group(1)
        year = int(match.group(2)) if match.group(2) else None
        return author, year

    match = re.match(r"(\d{4})", text)
    if match:
        return None, int(match.group(1))

    return None, None


def validate_citations(
    citations: List[Citation],
    references: List[Dict[str, Any]],
) -> Tuple[List[Citation], List[ReferenceValidation], List[CitationIssue]]:
    issues = []
    ref_validations = []

    ref_dois = extract_dois_from_references(references)

    for i, ref in enumerate(references):
        raw_text = ref.get("raw_text", "") if isinstance(ref, dict) else str(ref)
        doi = ref_dois.get(i)
        ref_validations.append(
            ReferenceValidation(
                raw_text=raw_text,
                cited_count=0,
                is_cited=False,
                doi=doi,
                is_valid_doi=bool(doi),
            )
        )

    matched_refs = set()
    for citation in citations:
        ref_idx, match_score = _match_citation_to_reference(citation, references)

        if ref_idx >= 0 and match_score > 0.3:
            citation.reference_index = ref_idx
            citation.is_resolved = True
            citation.confidence = max(citation.confidence, match_score)
            matched_refs.add(ref_idx)

            if 0 <= ref_idx < len(ref_validations):
                ref_validations[ref_idx].cited_count += 1
                ref_validations[ref_idx].is_cited = True
        else:
            issues.append(
                CitationIssue(
                    type=CitationIssueType.BROKEN_CITATION,
                    severity=CitationSeverity.WARNING,
                    message=f"Citation '{citation.raw_text}' could not be matched to any reference",
                    citation_id=citation.id,
                )
            )

    for i, ref_val in enumerate(ref_validations):
        if not ref_val.is_cited:
            issues.append(
                CitationIssue(
                    type=CitationIssueType.UNUSED_REFERENCE,
                    severity=CitationSeverity.WARNING,
                    message=f"Reference [{i+1}] is never cited in the text",
                    reference_index=i,
                )
            )

    seen_refs = {}
    for i, ref in enumerate(references):
        raw_text = ref.get("raw_text", "") if isinstance(ref, dict) else str(ref)
        norm = _normalize_text(raw_text)
        if norm in seen_refs:
            issues.append(
                CitationIssue(
                    type=CitationIssueType.DUPLICATE_REFERENCE,
                    severity=CitationSeverity.WARNING,
                    message=f"Reference [{i+1}] appears to be a duplicate of Reference [{seen_refs[norm]+1}]",
                    reference_index=i,
                )
            )
        else:
            seen_refs[norm] = i

    return citations, ref_validations, issues


def calculate_health_score(
    citations: List[Citation],
    references: List[ReferenceValidation],
    issues: List[CitationIssue],
) -> CitationHealthScore:
    total_citations = len(citations)
    total_references = len(references)
    resolved_citations = sum(1 for c in citations if c.is_resolved)
    uncited_references = sum(1 for r in references if not r.is_cited)
    duplicate_issues = sum(1 for i in issues if i.type == CitationIssueType.DUPLICATE_REFERENCE)
    broken_issues = sum(1 for i in issues if i.type == CitationIssueType.BROKEN_CITATION)
    refs_with_doi = sum(1 for r in references if r.doi)

    if total_citations == 0:
        reference_coverage = 0.0
    else:
        reference_coverage = (resolved_citations / total_citations) * 100

    if total_citations == 0:
        citation_validity = 0.0
    else:
        citation_validity = ((total_citations - broken_issues) / total_citations) * 100

    if total_references == 0:
        duplicate_score = 100.0
    else:
        duplicate_score = ((total_references - duplicate_issues) / total_references) * 100

    if total_citations == 0:
        broken_score = 0.0
    else:
        broken_score = ((total_citations - broken_issues) / total_citations) * 100

    if total_references == 0:
        doi_score = 0.0
    else:
        doi_score = (refs_with_doi / total_references) * 100

    overall = (
        reference_coverage * 0.25
        + citation_validity * 0.25
        + duplicate_score * 0.2
        + broken_score * 0.2
        + doi_score * 0.1
    )

    explanations = []
    if reference_coverage < 80:
        explanations.append(f"Only {reference_coverage:.0f}% of citations are resolved to references")
    if citation_validity < 90:
        explanations.append(f"{broken_issues} broken citation(s) detected")
    if duplicate_issues > 0:
        explanations.append(f"{duplicate_issues} duplicate reference(s) found")
    if doi_score < 50:
        explanations.append(f"Only {doi_score:.0f}% of references have DOIs")

    explanation = "; ".join(explanations) if explanations else "Citation quality is good"

    return CitationHealthScore(
        overall=round(overall, 1),
        reference_coverage=round(reference_coverage, 1),
        citation_validity=round(citation_validity, 1),
        duplicate_score=round(duplicate_score, 1),
        broken_score=round(broken_score, 1),
        doi_score=round(doi_score, 1),
        explanation=explanation,
    )
