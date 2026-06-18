import re
import requests
import time
from typing import Optional, Dict, Any


CROSSREF_API = "https://api.crossref.org/works"
OPENALEX_API = "https://api.openalex.org/works"
SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper"


def resolve_reference_doi(
    title: Optional[str] = None,
    authors: Optional[list] = None,
    year: Optional[int] = None,
    raw_text: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    if title:
        result = _resolve_via_crossref(title=title, authors=authors, year=year)
        if result:
            return result

        result = _resolve_via_openalex(title=title, authors=authors, year=year)
        if result:
            return result

    if raw_text:
        result = _resolve_via_crossref(query=raw_text)
        if result:
            return result

    return None


def _resolve_via_crossref(
    title: Optional[str] = None,
    query: Optional[str] = None,
    authors: Optional[list] = None,
    year: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    try:
        params = {"rows": 3}
        if title:
            params["query.title"] = title
        elif query:
            params["query.bibliographic"] = query

        if authors:
            params["query.author"] = ", ".join(authors[:3])
        if year:
            params["filter"] = f"from-pub-date:{year-1},until-pub-date:{year+1}"

        response = requests.get(CROSSREF_API, params=params, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        items = data.get("message", {}).get("items", [])
        if not items:
            return None

        best = items[0]
        doi = best.get("DOI", "")
        title = best.get("title", [""])[0] if best.get("title") else ""
        authors = [
            a.get("given", "") + " " + a.get("family", "")
            for a in best.get("author", [])
        ]
        journal = best.get("container-title", [""])[0] if best.get("container-title") else ""
        year = None
        if "published-print" in best:
            date_parts = best["published-print"].get("date-parts", [[]])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]
        elif "published-online" in best:
            date_parts = best["published-online"].get("date-parts", [[]])
            if date_parts and date_parts[0]:
                year = date_parts[0][0]

        return {
            "doi": doi,
            "title": title,
            "authors": [a.strip() for a in authors if a.strip()],
            "year": year,
            "journal": journal,
            "source": "crossref",
        }

    except Exception:
        return None


def _resolve_via_openalex(
    title: Optional[str] = None,
    query: Optional[str] = None,
    authors: Optional[list] = None,
    year: Optional[int] = None,
) -> Optional[Dict[str, Any]]:
    try:
        search_text = title or query or ""
        params = {"search": search_text, "per_page": 3}

        if year:
            params["filter"] = f"publication_year:{year}"

        response = requests.get(OPENALEX_API, params=params, timeout=10)
        if response.status_code != 200:
            return None

        data = response.json()
        results = data.get("results", [])
        if not results:
            return None

        best = results[0]
        doi = best.get("doi", "")
        if doi and doi.startswith("https://doi.org/"):
            doi = doi[16:]

        title = best.get("title", "")
        authors = [
            a.get("author", {}).get("display_name", "")
            for a in best.get("authorships", [])
        ]
        journal = ""
        if best.get("primary_location", {}).get("source"):
            journal = best["primary_location"]["source"].get("display_name", "")
        year = best.get("publication_year")

        return {
            "doi": doi,
            "title": title,
            "authors": [a.strip() for a in authors if a.strip()],
            "year": year,
            "journal": journal,
            "source": "openalex",
        }

    except Exception:
        return None


def validate_doi(doi: str) -> bool:
    try:
        url = f"https://doi.org/{doi}"
        response = requests.head(url, timeout=10, allow_redirects=True)
        return response.status_code == 200
    except Exception:
        return False
