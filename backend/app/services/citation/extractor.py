import re
import uuid
from typing import List, Dict, Any, Optional, Tuple

from app.services.citation.schema import Citation, CitationType
from app.services.citation.rules import (
    NUMERIC_PATTERNS,
    AUTHOR_YEAR_PATTERNS,
    LATEX_CITATION_PATTERNS,
    get_all_citation_patterns,
)


def _normalize_citation_id(raw: str) -> str:
    cleaned = re.sub(r"[\s\[\]\(\)]", "", raw)
    return cleaned.lower()


def _extract_numeric_numbers(citation_text: str) -> List[str]:
    match = re.search(r"(\d+(?:\s*,\s*\d+)*)", citation_text)
    if match:
        return [n.strip() for n in match.group(1).split(",")]
    return []


def _extract_author_year_parts(citation_text: str) -> Tuple[Optional[str], Optional[str]]:
    text = citation_text.strip()
    text = re.sub(r"[\(\)]", "", text)

    match = re.match(
        r"([A-Z][a-z]+(?:\s+(?:et\s+al\.?|and\s+[A-Z][a-z]+))*)(?:,\s*)?(\d{4})?",
        text,
    )
    if match:
        author = match.group(1)
        year = match.group(2)
        return author, year
    return None, None


def extract_citations_from_text(
    text: str,
    source_section: str = "",
) -> List[Citation]:
    if not text:
        return []

    seen = set()
    citations = []

    for pattern in get_all_citation_patterns():
        for match in re.finditer(pattern.regex, text):
            raw = match.group(0)
            norm_id = _normalize_citation_id(raw)

            if norm_id in seen:
                continue
            seen.add(norm_id)

            citation_type = CitationType.UNKNOWN
            if pattern in NUMERIC_PATTERNS or pattern in LATEX_CITATION_PATTERNS:
                citation_type = CitationType.NUMERIC
            elif pattern in AUTHOR_YEAR_PATTERNS:
                citation_type = CitationType.AUTHOR_YEAR

            citation = Citation(
                id=str(uuid.uuid4())[:8],
                raw_text=raw,
                type=citation_type,
                source_section=source_section,
                confidence=pattern.confidence,
                position_start=match.start(),
                position_end=match.end(),
            )
            citations.append(citation)

    return citations


def extract_citations_from_sections(
    sections: List[Dict[str, Any]],
) -> List[Citation]:
    all_citations = []

    for section in sections:
        heading = section.get("heading", "")
        content = section.get("content", "")
        label = section.get("label", "")

        section_citations = extract_citations_from_text(
            content, source_section=label or heading
        )
        all_citations.extend(section_citations)

    return all_citations


def extract_citations_from_structured(
    structured_json: Dict[str, Any],
) -> List[Citation]:
    sections = structured_json.get("sections", [])
    citations = extract_citations_from_sections(sections)

    abstract = structured_json.get("abstract", "")
    if abstract:
        abstract_citations = extract_citations_from_text(abstract, source_section="abstract")
        existing_ids = {c.raw_text for c in citations}
        for c in abstract_citations:
            if c.raw_text not in existing_ids:
                citations.append(c)

    return citations


def extract_dois_from_text(text: str) -> List[str]:
    dois = []

    for match in re.finditer(r"10\.\d{4,}/[^\s\)\],;]+", text):
        doi = match.group(0).rstrip(".,;)")
        dois.append(doi)

    return list(set(dois))


def extract_dois_from_references(
    references: List[Dict[str, Any]],
) -> Dict[int, Optional[str]]:
    ref_dois = {}

    for i, ref in enumerate(references):
        raw_text = ref.get("raw_text", "") if isinstance(ref, dict) else str(ref)
        dois = extract_dois_from_text(raw_text)
        ref_dois[i] = dois[0] if dois else None

    return ref_dois
