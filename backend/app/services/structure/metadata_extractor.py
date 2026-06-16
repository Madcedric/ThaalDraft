import re
from typing import Any, Dict, List, Optional

from app.services.structure.schema import Author, Reference, DocumentMetadata


def _extract_doi(text: str) -> Optional[str]:
    doi_patterns = [
        r"(?:doi[:\s]*)(10\.\d{4,}/[^\s]+)",
        r"(?:DOI[:\s]*)(10\.\d{4,}/[^\s]+)",
        r"(https?://doi\.org/10\.\d{4,}/[^\s]+)",
        r"(10\.\d{4,}/[^\s]+)",
    ]
    for pattern in doi_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            doi = match.group(1).rstrip(".,;)")
            return doi
    return None


def _extract_year(text: str) -> Optional[int]:
    match = re.search(r"\b(19|20)\d{2}\b", text)
    if match:
        return int(match.group(0))
    return None


def _extract_reference_parts(raw: str) -> Reference:
    ref = Reference(raw_text=raw)

    doi = _extract_doi(raw)
    if doi:
        ref.doi = doi

    year = _extract_year(raw)
    if year:
        ref.year = year

    author_match = re.match(
        r"^([A-Z][a-z]+(?:\s+(?:et\s+al\.?|and\s+[A-Z][a-z]+))*(?:,\s*[A-Z][a-z]+)*)",
        raw,
    )
    if author_match:
        author_text = author_match.group(1)
        ref.authors = [a.strip() for a in re.split(r",\s*and\s+|,\s*", author_text)]

    title_match = re.search(r'"([^"]+)"', raw)
    if not title_match:
        title_match = re.search(r"\.\s+([A-Z][^.]{10,80})\.", raw)
    if title_match:
        ref.title = title_match.group(1).strip()

    vol_match = re.search(r"(?:vol\.?|volume)\s*(\d+)", raw, re.IGNORECASE)
    if vol_match:
        ref.volume = vol_match.group(1)

    pages_match = re.search(r"(?:pp\.?|pages?)\s*(\d+[-–]\d+)", raw, re.IGNORECASE)
    if pages_match:
        ref.pages = pages_match.group(1)

    journal_match = re.search(
        r"(?:in|journal\s+)([A-Z][a-zA-Z\s&]+(?:Journal|Transactions|Proceedings|Letters|Review))",
        raw,
        re.IGNORECASE,
    )
    if journal_match:
        ref.journal = journal_match.group(1).strip()

    return ref


def _parse_authors(raw_authors: Any) -> List[Author]:
    if not raw_authors:
        return []

    if isinstance(raw_authors, list):
        authors = []
        for item in raw_authors:
            if isinstance(item, dict):
                authors.append(
                    Author(
                        name=item.get("name", ""),
                        affiliation=item.get("affiliation"),
                        email=item.get("email"),
                    )
                )
            elif isinstance(item, str):
                email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", item)
                email = email_match.group(0) if email_match else None
                clean_name = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "", item).strip().rstrip(", ")
                if clean_name:
                    authors.append(Author(name=clean_name, email=email))
        return authors

    if isinstance(raw_authors, str):
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.]+", raw_authors)
        email = email_match.group(0) if email_match else None
        clean_name = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "", raw_authors).strip()
        if clean_name:
            parts = re.split(r"\s+and\s+|,\s*", clean_name)
            return [Author(name=p.strip(), email=email) for p in parts if p.strip()]

    return []


def _extract_keywords(text: str) -> List[str]:
    if not text:
        return []

    kw_match = re.search(
        r"(?:keywords?|key\s+words?)[:\s]*(.+?)(?:\n\n|\.\s|\Z)",
        text,
        re.IGNORECASE | re.DOTALL,
    )
    if kw_match:
        kw_text = kw_match.group(1).strip()
        keywords = re.split(r"[;,]\s*|\s+and\s+", kw_text)
        return [kw.strip() for kw in keywords if kw.strip() and len(kw.strip()) > 1]

    return []


def _count_words(text: str) -> int:
    if not text:
        return 0
    return len(text.split())


def extract_metadata(parsed: Dict[str, Any]) -> DocumentMetadata:
    title = parsed.get("title", "")
    raw_authors = parsed.get("authors", [])
    abstract = parsed.get("abstract", "")
    sections = parsed.get("sections", [])
    references = parsed.get("references", [])
    figures = parsed.get("figures", [])

    authors = _parse_authors(raw_authors)

    all_text = " ".join(
        s.get("content", "") if isinstance(s, dict) else getattr(s, "content", "")
        for s in sections
    )
    full_text = f"{title} {abstract} {all_text}"
    word_count = _count_words(full_text)

    keywords = _extract_keywords(full_text)
    if not keywords:
        keywords = _extract_keywords(abstract)

    doi = _extract_doi(full_text)

    has_abstract = bool(abstract and len(abstract.strip()) > 10)
    has_references = bool(references)

    section_count = len(sections)
    reference_count = len(references)

    return DocumentMetadata(
        doi=doi,
        keywords=keywords,
        word_count=word_count,
        section_count=section_count,
        reference_count=reference_count,
        has_abstract=has_abstract,
        has_references=has_references,
        has_keywords=bool(keywords),
    )


def extract_references(parsed: Dict[str, Any]) -> List[Reference]:
    raw_refs = parsed.get("references", [])
    if not raw_refs:
        return []

    references = []
    for ref_text in raw_refs:
        if isinstance(ref_text, str) and ref_text.strip():
            references.append(_extract_reference_parts(ref_text.strip()))
        elif isinstance(ref_text, dict):
            references.append(
                Reference(
                    raw_text=ref_text.get("text", str(ref_text)),
                    doi=ref_text.get("doi"),
                    title=ref_text.get("title"),
                    year=ref_text.get("year"),
                )
            )

    return references
