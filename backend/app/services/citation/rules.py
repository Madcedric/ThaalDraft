import re
from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class CitationPattern:
    name: str
    regex: str
    confidence: float
    group_index: int = 0


NUMERIC_PATTERNS = [
    CitationPattern(
        name="numeric_bracket",
        regex=r"\[(\d+(?:\s*,\s*\d+)*)\]",
        confidence=0.95,
    ),
    CitationPattern(
        name="numeric_paren",
        regex=r"\((\d+(?:\s*,\s*\d+)*)\)",
        confidence=0.85,
    ),
    CitationPattern(
        name="numeric_superscript",
        regex=r"(\d+)(?:\s*et\s+al\.?)",
        confidence=0.7,
    ),
]

AUTHOR_YEAR_PATTERNS = [
    CitationPattern(
        name="author_year_paren",
        regex=r"\(([A-Z][a-z]+(?:\s+(?:et\s+al\.?|and\s+[A-Z][a-z]+))*(?:,\s*\d{4})?)\)",
        confidence=0.9,
    ),
    CitationPattern(
        name="author_year_text",
        regex=r"([A-Z][a-z]+(?:\s+(?:et\s+al\.?|and\s+[Za-z]+))?),?\s+(\d{4})",
        confidence=0.85,
    ),
    CitationPattern(
        name="author_year_bracket",
        regex=r"\[([A-Z][a-z]+(?:\s+et\s+al\.?)?,?\s*\d{4})\]",
        confidence=0.8,
    ),
]

LATEX_CITATION_PATTERNS = [
    CitationPattern(
        name="latex_cite",
        regex=r"\\cite\{([^}]+)\}",
        confidence=0.95,
    ),
    CitationPattern(
        name="latex_citep",
        regex=r"\\citep\{([^}]+)\}",
        confidence=0.95,
    ),
    CitationPattern(
        name="latex_citet",
        regex=r"\\citet\{([^}]+)\}",
        confidence=0.95,
    ),
]

DOI_PATTERN = re.compile(
    r"(?:doi[:\s]*)(10\.\d{4,}/[^\s]+)",
    re.IGNORECASE,
)
DOI_URL_PATTERN = re.compile(
    r"https?://doi\.org/(10\.\d{4,}/[^\s]+)",
    re.IGNORECASE,
)

REFERENCE_SECTIONS = {"references", "bibliography", "works cited", "citations"}


def get_all_citation_patterns() -> List[CitationPattern]:
    return NUMERIC_PATTERNS + AUTHOR_YEAR_PATTERNS + LATEX_CITATION_PATTERNS


def detect_citation_style(citations: List[str]) -> str:
    numeric_count = 0
    author_year_count = 0

    for c in citations:
        for pattern in NUMERIC_PATTERNS:
            if re.match(pattern.regex, c):
                numeric_count += 1
                break
        for pattern in AUTHOR_YEAR_PATTERNS:
            if re.match(pattern.regex, c):
                author_year_count += 1
                break

    total = numeric_count + author_year_count
    if total == 0:
        return "unknown"

    if numeric_count / total > 0.7:
        return "ieee"
    if author_year_count / total > 0.7:
        return "apa"
    return "mixed"
