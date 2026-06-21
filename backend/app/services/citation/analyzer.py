import time
import logging
from typing import Dict, Any, List

from app.services.citation.schema import (
    CitationReport,
    CitationStyle,
)
from app.services.citation.extractor import (
    extract_citations_from_structured,
    extract_dois_from_references,
)
from app.services.citation.validator import (
    validate_citations,
    calculate_health_score,
)
from app.services.citation.rules import detect_citation_style
from app.services.citation.resolver import resolve_reference_doi

logger = logging.getLogger(__name__)


def analyze_citations(
    structured_json,
    document_id: str = "",
    resolve_dois: bool = False,
) -> CitationReport:
    if hasattr(structured_json, 'model_dump'):
        structured_json = structured_json.model_dump()

    start_time = time.time()
    api_calls = 0

    citations = extract_citations_from_structured(structured_json)
    references = structured_json.get("references", [])

    citation_texts = [c.raw_text for c in citations]
    citation_style_str = detect_citation_style(citation_texts)
    try:
        citation_style = CitationStyle(citation_style_str)
    except ValueError:
        citation_style = CitationStyle.UNKNOWN

    citations, ref_validations, issues = validate_citations(citations, references)

    if resolve_dois:
        max_doi_resolves = 10
        doi_count = 0
        for i, ref_val in enumerate(ref_validations):
            if doi_count >= max_doi_resolves:
                logger.info(f"DOI resolution: hit limit of {max_doi_resolves}, skipping remaining")
                break
            if not ref_val.doi and ref_val.raw_text:
                try:
                    result = resolve_reference_doi(raw_text=ref_val.raw_text)
                    api_calls += 1
                    doi_count += 1
                    if result and result.get("doi"):
                        ref_validations[i].doi = result["doi"]
                        ref_validations[i].is_valid_doi = True
                        if result.get("title"):
                            ref_validations[i].title = result["title"]
                        if result.get("authors"):
                            ref_validations[i].authors = result["authors"]
                        if result.get("year"):
                            ref_validations[i].year = result["year"]
                        if result.get("journal"):
                            ref_validations[i].journal = result["journal"]
                except Exception as e:
                    logger.warning(f"DOI resolution failed for reference {i}: {e}")

    health_score = calculate_health_score(citations, ref_validations, issues)

    resolved_count = sum(1 for c in citations if c.is_resolved)
    unresolved_count = len(citations) - resolved_count

    processing_time = (time.time() - start_time) * 1000

    report = CitationReport(
        document_id=document_id,
        citation_style=citation_style,
        total_citations=len(citations),
        total_references=len(ref_validations),
        resolved_citations=resolved_count,
        unresolved_citations=unresolved_count,
        citations=citations,
        references=ref_validations,
        issues=issues,
        health_score=health_score,
        processing_metadata={
            "processing_time_ms": round(processing_time, 2),
            "external_api_calls": api_calls,
        },
    )

    return report
