"""DOI Intelligence Resolver — V2.

Unified DOI resolution with fallback chain:
CrossRef → OpenAlex → Semantic Scholar

Also provides reference enrichment (fill in missing metadata).
"""

import logging
import time
from typing import Any, Dict, List, Optional

from app.services.citation.resolver import resolve_reference_doi
from app.services.doi_intelligence.semantic_scholar import SemanticScholarClient

logger = logging.getLogger(__name__)


def resolve_doi(
    title: Optional[str] = None,
    authors: Optional[List[str]] = None,
    year: Optional[int] = None,
    raw_text: Optional[str] = None,
    doi: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Resolve a reference to DOI metadata using the full intelligence chain.

    Fallback order: CrossRef → OpenAlex → Semantic Scholar

    Returns:
        Dict with doi, title, authors, year, journal, source or None.
    """
    # If DOI is already provided, validate and enrich
    if doi:
        result = _validate_and_enrich_doi(doi)
        if result:
            return result

    # Try CrossRef/OpenAlex via existing resolver
    result = resolve_reference_doi(
        title=title,
        authors=authors,
        year=year,
        raw_text=raw_text,
    )
    if result:
        return result

    # Fallback: Semantic Scholar
    ss = SemanticScholarClient()
    if ss.is_available:
        result = ss.search_paper(title=title, raw_text=raw_text)
        if result:
            return result

    return None


def _validate_and_enrich_doi(doi: str) -> Optional[Dict[str, Any]]:
    """Validate a DOI and enrich with metadata from multiple sources."""
    # Try Semantic Scholar first (fastest for DOI lookup)
    ss = SemanticScholarClient()
    if ss.is_available:
        result = ss.search_paper(doi=doi)
        if result:
            return result

    # Fallback: CrossRef
    result = resolve_reference_doi(raw_text=f"DOI:{doi}")
    if result:
        return result

    return None


def enrich_references(
    references: List[Dict[str, Any]],
    max_enrichments: int = 20,
    timeout_per_ref: float = 5.0,
) -> List[Dict[str, Any]]:
    """Enrich a list of references with metadata from external APIs.

    Args:
        references: List of reference dicts (must have 'raw_text' or 'doi').
        max_enrichments: Maximum number of references to enrich.
        timeout_per_ref: Timeout per reference in seconds.

    Returns:
        List of enriched reference dicts.
    """
    enriched = []
    enrichment_count = 0

    for ref in references:
        if enrichment_count >= max_enrichments:
            enriched.append(ref)
            continue

        raw_text = ref.get("raw_text", "")
        doi = ref.get("doi")
        title = ref.get("title")

        start = time.time()
        try:
            result = resolve_doi(
                title=title,
                raw_text=raw_text,
                doi=doi,
            )
            if result and result.get("doi"):
                # Merge enriched metadata
                enriched_ref = {**ref}
                if not enriched_ref.get("doi"):
                    enriched_ref["doi"] = result["doi"]
                if not enriched_ref.get("title") and result.get("title"):
                    enriched_ref["title"] = result["title"]
                if not enriched_ref.get("authors") and result.get("authors"):
                    enriched_ref["authors"] = result["authors"]
                if not enriched_ref.get("year") and result.get("year"):
                    enriched_ref["year"] = result["year"]
                if not enriched_ref.get("journal") and result.get("journal"):
                    enriched_ref["journal"] = result["journal"]
                enriched_ref["enrichment_source"] = result.get("source", "unknown")
                enriched.append(enriched_ref)
                enrichment_count += 1
            else:
                enriched.append(ref)
        except Exception as e:
            logger.warning(f"Enrichment failed for reference: {e}")
            enriched.append(ref)

        elapsed = time.time() - start
        if elapsed > timeout_per_ref:
            logger.warning(f"Enrichment timeout ({elapsed:.1f}s) for reference")

    logger.info(f"Enriched {enrichment_count}/{len(references)} references")
    return enriched
