"""Structure Intelligence Engine.

Uses spaCy NER, keyword analysis, and positional heuristics to:
- Detect section types from headings AND content
- Extract tables and figures
- Classify references
- Build a StructuredManuscript from raw parsed data
"""
import re
import uuid
import logging
from typing import Any, Dict, List, Optional, Tuple

from app.services.manuscript.model import (
    StructuredManuscript,
    ManuscriptSection,
    SectionType,
    Author,
    Reference,
    Table,
    Figure,
)

logger = logging.getLogger(__name__)

_spacy_nlp = None


def _get_spacy():
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            import spacy
            logger.info("Loading spaCy model (first call, may take ~15s)...")
            _spacy_nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy model loaded")
        except Exception:
            logger.warning("spaCy en_core_web_sm not available")
    return _spacy_nlp


# Pre-load spaCy at module import so cold start happens at boot, not first request
try:
    _ = _get_spacy()
except Exception:
    pass


HEADING_LABEL_MAP = {
    "abstract": SectionType.ABSTRACT,
    "introduction": SectionType.INTRODUCTION,
    "related work": SectionType.RELATED_WORK,
    "related works": SectionType.RELATED_WORK,
    "background": SectionType.RELATED_WORK,
    "literature review": SectionType.RELATED_WORK,
    "methodology": SectionType.METHODOLOGY,
    "methods": SectionType.METHODS,
    "method": SectionType.METHODS,
    "approach": SectionType.METHODS,
    "proposed method": SectionType.METHODS,
    "proposed approach": SectionType.METHODS,
    "material and methods": SectionType.METHODS,
    "materials and methods": SectionType.METHODS,
    "experimental setup": SectionType.EXPERIMENTS,
    "experiments": SectionType.EXPERIMENTS,
    "experiment": SectionType.EXPERIMENTS,
    "evaluation": SectionType.EXPERIMENTS,
    "experimental results": SectionType.RESULTS,
    "results": SectionType.RESULTS,
    "results and discussion": SectionType.DISCUSSION,
    "discussion": SectionType.DISCUSSION,
    "analysis": SectionType.DISCUSSION,
    "conclusion": SectionType.CONCLUSION,
    "conclusions": SectionType.CONCLUSIONS,
    "summary": SectionType.CONCLUSION,
    "concluding remarks": SectionType.CONCLUSION,
    "references": SectionType.REFERENCES,
    "bibliography": SectionType.REFERENCES,
    "works cited": SectionType.REFERENCES,
    "acknowledgments": SectionType.ACKNOWLEDGMENTS,
    "acknowledgements": SectionType.ACKNOWLEDGMENTS,
    "appendix": SectionType.APPENDIX,
}

CONTENT_SIGNALS = {
    SectionType.INTRODUCTION: [
        "in this paper", "we propose", "we present", "our approach",
        "the rest of the paper", "this work", "motivation", "objective",
        "contribution", "novel", "first time",
    ],
    SectionType.METHODOLOGY: [
        "we use", "our method", "algorithm", "approach", "framework",
        "we employ", "we implement", "pipeline", "architecture",
        "training", "preprocessing",
    ],
    SectionType.RESULTS: [
        "achieve", "accuracy", "performance", "outperform", "baseline",
        "comparison", "evaluation metric", "table shows", "figure shows",
        "result", "demonstrate",
    ],
    SectionType.DISCUSSION: [
        "we observe", "interesting", "limitation", "future work",
        "implication", "interpret", "however", "trade-off",
    ],
    SectionType.CONCLUSION: [
        "in conclusion", "we have shown", "we have presented",
        "summary of", "future direction", "concluding",
    ],
}


def _normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", text.lower().strip())


def classify_heading(heading: str, content: str = "", position_ratio: float = 0.0) -> Tuple[SectionType, float]:
    """Classify a section heading into a SectionType with confidence."""
    norm = _normalize(heading)

    # Exact match
    if norm in HEADING_LABEL_MAP:
        return HEADING_LABEL_MAP[norm], 0.95

    # Partial keyword match
    best_label = SectionType.OTHER
    best_score = 0.0
    for key, label in HEADING_LABEL_MAP.items():
        if key in norm or norm in key:
            score = 0.8
            if score > best_score:
                best_label = label
                best_score = score

    # Content-based signals
    if content and best_score < 0.7:
        content_lower = content.lower()
        for label, signals in CONTENT_SIGNALS.items():
            matches = sum(1 for s in signals if s in content_lower)
            if matches >= 2:
                score = 0.5 + min(matches * 0.05, 0.2)
                if score > best_score:
                    best_label = label
                    best_score = score

    return best_label, best_score


def extract_tables_from_text(text: str) -> List[Table]:
    """Extract table-like structures from text."""
    tables = []
    table_pattern = r"(?:Table\s+\d+|TABLE\s+\d+)"
    for match in re.finditer(table_pattern, text):
        table_id = str(uuid.uuid4())[:8]
        tables.append(Table(
            id=f"table_{table_id}",
            caption=match.group(0),
            position=match.group(0),
        ))
    return tables


def extract_figures_from_text(text: str) -> List[Figure]:
    """Extract figure references from text."""
    figures = []
    fig_pattern = r"(?:Fig(?:ure)?\.?\s+\d+|FIGURE?\s+\d+)"
    for match in re.finditer(fig_pattern, text):
        fig_id = str(uuid.uuid4())[:8]
        figures.append(Figure(
            id=f"fig_{fig_id}",
            caption=match.group(0),
            position=match.group(0),
        ))
    return figures


def parse_reference(raw_text: str, index: int) -> Reference:
    """Parse a raw reference string into a structured Reference."""
    ref = Reference(index=index, raw_text=raw_text)

    # Extract DOI
    doi_match = re.search(r"10\.\d{4,}/[^\s\)\],;]+", raw_text)
    if doi_match:
        ref.doi = doi_match.group(0).rstrip(".,;)")

    # Extract year
    year_match = re.search(r"\b(19|20)\d{2}\b", raw_text)
    if year_match:
        ref.year = int(year_match.group(0))

    # Extract title (text in quotes or after a period)
    title_match = re.search(r'["\u201c](.+?)["\u201d]', raw_text)
    if title_match:
        ref.title = title_match.group(1)
    else:
        parts = re.split(r"\.\s", raw_text)
        if len(parts) > 1:
            ref.title = parts[1].strip().rstrip(".")

    return ref


def extract_authors_from_text(text: str) -> List[Author]:
    """Extract author names using spaCy NER."""
    nlp = _get_spacy()
    if not nlp:
        return []

    doc = nlp(text[:2000])
    authors = []
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            name = ent.text.strip()
            if len(name.split()) >= 2 and name not in [a.name for a in authors]:
                authors.append(Author(name=name))
    return authors


def build_manuscript(raw_data: Dict[str, Any]) -> StructuredManuscript:
    """Build a StructuredManuscript from raw parsed data.

    This is the core intelligence engine that:
    1. Classifies sections using heading + content + position
    2. Extracts tables and figures from content
    3. Parses references into structured format
    4. Extracts authors via NER
    """
    title = raw_data.get("title", "")
    abstract = raw_data.get("abstract", "")
    keywords = raw_data.get("keywords", [])

    # Extract authors
    raw_authors = raw_data.get("authors", [])
    authors = []
    for a in raw_authors:
        if isinstance(a, dict):
            authors.append(Author(
                name=a.get("name", str(a)),
                affiliation=a.get("affiliation"),
                email=a.get("email"),
            ))
        elif isinstance(a, str):
            authors.append(Author(name=a))

    if not authors and title:
        authors = extract_authors_from_text(title)

    # Process sections
    sections = []
    all_tables = []
    all_figures = []
    raw_sections = raw_data.get("sections", [])
    total_sections = len(raw_sections)

    for idx, sec in enumerate(raw_sections):
        heading = sec.get("heading", "") if isinstance(sec, dict) else ""
        content = sec.get("content", "") if isinstance(sec, dict) else ""

        position_ratio = idx / max(total_sections, 1)
        label, confidence = classify_heading(heading, content, position_ratio)

        # Extract tables and figures from content
        sec_tables = extract_tables_from_text(content)
        sec_figures = extract_figures_from_text(content)
        all_tables.extend(sec_tables)
        all_figures.extend(sec_figures)

        sections.append(ManuscriptSection(
            id=str(uuid.uuid4())[:8],
            heading=heading or "Untitled",
            label=label,
            content=content,
            level=sec.get("level", 1) if isinstance(sec, dict) else 1,
            confidence=confidence,
            tables=sec_tables,
            figures=sec_figures,
        ))

    # Add abstract as a section if not already present
    if abstract and not any(s.label == SectionType.ABSTRACT for s in sections):
        sections.insert(0, ManuscriptSection(
            id=str(uuid.uuid4())[:8],
            heading="Abstract",
            label=SectionType.ABSTRACT,
            content=abstract,
            level=1,
            confidence=1.0,
        ))

    # Parse references
    references = []
    raw_refs = raw_data.get("references", [])
    for idx, ref in enumerate(raw_refs):
        raw_text = ref.get("raw_text", str(ref)) if isinstance(ref, dict) else str(ref)
        references.append(parse_reference(raw_text, idx + 1))

    # Word count
    word_count = len(abstract.split()) if abstract else 0
    for s in sections:
        word_count += len(s.content.split())

    return StructuredManuscript(
        title=title,
        authors=authors,
        abstract=abstract,
        keywords=keywords,
        sections=sections,
        references=references,
        tables=all_tables,
        figures=all_figures,
        word_count=word_count,
        section_count=len(sections),
        reference_count=len(references),
        metadata=raw_data.get("metadata", {}),
    )
