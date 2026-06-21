"""DOI Intelligence Module — V2.

Provides DOI resolution, validation, and enrichment using:
- CrossRef
- OpenAlex
- Semantic Scholar
"""

from app.services.doi_intelligence.resolver import resolve_doi, enrich_references
from app.services.doi_intelligence.semantic_scholar import SemanticScholarClient

__all__ = ["resolve_doi", "enrich_references", "SemanticScholarClient"]
