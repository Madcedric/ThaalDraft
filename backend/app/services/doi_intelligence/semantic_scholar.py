"""Semantic Scholar API client — V2 DOI Intelligence.

Integrates with Semantic Scholar for paper metadata enrichment.
API: https://api.semanticscholar.org/graph/v1/paper
"""

import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests

logger = logging.getLogger(__name__)

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1"
SEMANTIC_SCHOLAR_TIMEOUT = int(os.environ.get("SEMANTIC_SCHOLAR_TIMEOUT", "10"))


class SemanticScholarClient:
    """Client for Semantic Scholar API."""

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")
        self.base_url = SEMANTIC_SCHOLAR_API
        self.timeout = SEMANTIC_SCHOLAR_TIMEOUT

    @property
    def is_available(self) -> bool:
        """Check if Semantic Scholar API is reachable."""
        try:
            resp = requests.get(
                f"{self.base_url}/paper/DOI:10.1038/nature14539",
                params={"fields": "title"},
                headers=self._headers(),
                timeout=5,
            )
            return resp.status_code == 200
        except Exception:
            return False

    def search_paper(
        self,
        query: Optional[str] = None,
        doi: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Optional[Dict[str, Any]]:
        """Search for a paper by query, DOI, or title.

        Returns paper metadata or None if not found.
        """
        try:
            if doi:
                return self._get_by_doi(doi)
            elif title:
                return self._search_by_title(title)
            elif query:
                return self._search_by_query(query)
        except Exception as e:
            logger.warning(f"Semantic Scholar search failed: {e}")
        return None

    def _get_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """Get paper by DOI."""
        fields = "title,authors,year,venue,citationCount,externalIds,abstract,publicationDate"
        resp = requests.get(
            f"{self.base_url}/paper/DOI:{doi}",
            params={"fields": fields},
            headers=self._headers(),
            timeout=self.timeout,
        )
        if resp.status_code == 200:
            return self._parse_paper(resp.json())
        return None

    def _search_by_title(self, title: str) -> Optional[Dict[str, Any]]:
        """Search by title."""
        resp = requests.get(
            f"{self.base_url}/paper/search",
            params={"query": title, "limit": 3, "fields": "title,authors,year,venue,citationCount,externalIds,abstract"},
            headers=self._headers(),
            timeout=self.timeout,
        )
        if resp.status_code == 200:
            data = resp.json()
            papers = data.get("data", [])
            if papers:
                return self._parse_paper(papers[0])
        return None

    def _search_by_query(self, query: str) -> Optional[Dict[str, Any]]:
        """Search by free-form query."""
        return self._search_by_title(query)

    def _parse_paper(self, paper: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Semantic Scholar paper response into standard format."""
        authors = [
            a.get("name", "") for a in paper.get("authors", []) if a.get("name")
        ]
        external_ids = paper.get("externalIds") or {}
        doi = external_ids.get("DOI", "")

        return {
            "doi": doi,
            "title": paper.get("title", ""),
            "authors": authors,
            "year": paper.get("year"),
            "journal": paper.get("venue", ""),
            "citation_count": paper.get("citationCount", 0),
            "abstract": paper.get("abstract", ""),
            "publication_date": paper.get("publicationDate"),
            "source": "semantic_scholar",
        }

    def enrich_reference(self, raw_text: str, doi: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Enrich a reference with Semantic Scholar metadata."""
        if doi:
            return self._get_by_doi(doi)
        return self._search_by_title(raw_text[:200])

    def _headers(self) -> Dict[str, str]:
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["x-api-key"] = self.api_key
        return headers
