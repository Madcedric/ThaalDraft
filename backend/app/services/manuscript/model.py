"""Structured Manuscript Model — V2 Canonical.

Canonical data model for representing a parsed manuscript.
All downstream engines (formatting, review, export, compliance, DOI) operate on this model.

This is the SINGLE SOURCE OF TRUTH for the system.
"""

import uuid
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from enum import Enum


class SectionType(str, Enum):
    TITLE = "title"
    ABSTRACT = "abstract"
    KEYWORDS = "keywords"
    INTRODUCTION = "introduction"
    RELATED_WORK = "related_work"
    METHODOLOGY = "methodology"
    METHODS = "methods"
    EXPERIMENTS = "experiments"
    RESULTS = "results"
    DISCUSSION = "discussion"
    CONCLUSION = "conclusion"
    CONCLUSIONS = "conclusions"
    REFERENCES = "references"
    ACKNOWLEDGMENTS = "acknowledgments"
    APPENDIX = "appendix"
    OTHER = "other"


def _new_id() -> str:
    return str(uuid.uuid4())[:8]


# ─── Core Sub-Models ──────────────────────────────────────────────────────────


class Author(BaseModel):
    """A manuscript author with optional affiliation metadata."""
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None
    orcid: Optional[str] = None


class Reference(BaseModel):
    """A bibliographic reference."""
    index: int = 0
    raw_text: str = ""
    authors: List[str] = Field(default_factory=list)
    title: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    doi: Optional[str] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    url: Optional[str] = None


class Table(BaseModel):
    """A table extracted from the manuscript."""
    id: str = Field(default_factory=_new_id)
    caption: Optional[str] = None
    headers: List[str] = Field(default_factory=list)
    rows: List[List[str]] = Field(default_factory=list)
    position: Optional[str] = None
    section_label: Optional[str] = None


class Figure(BaseModel):
    """A figure extracted from the manuscript."""
    id: str = Field(default_factory=_new_id)
    caption: Optional[str] = None
    image_path: Optional[str] = None
    position: Optional[str] = None
    section_label: Optional[str] = None

    @field_validator("caption", mode="before")
    @classmethod
    def caption_from_string(cls, v: Any) -> Any:
        if isinstance(v, str):
            return v
        return v


class ManuscriptSection(BaseModel):
    """A section of the manuscript."""
    id: str = Field(default_factory=_new_id)
    heading: str = ""
    label: SectionType = SectionType.OTHER
    content: str = ""
    level: int = 1
    confidence: float = 0.0
    tables: List[Table] = Field(default_factory=list)
    figures: List[Figure] = Field(default_factory=list)
    subsections: List["ManuscriptSection"] = Field(default_factory=list)


# ─── V2 New Sub-Models ────────────────────────────────────────────────────────


class CitationMap(BaseModel):
    """Mapping of in-text citations to their references."""
    in_text_markers: List[str] = Field(default_factory=list)
    total_citations: int = 0
    resolved_citations: int = 0
    unresolved_citations: int = 0
    citation_style: Optional[str] = None


class DOIRecord(BaseModel):
    """DOI resolution record for a reference."""
    reference_index: int = 0
    doi: str = ""
    source: str = "crossref"
    resolved: bool = False
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ComplianceReport(BaseModel):
    """Journal compliance report."""
    journal_id: Optional[str] = None
    journal_name: Optional[str] = None
    score: float = 0.0
    checks_performed: int = 0
    checks_passed: int = 0
    checks_failed: int = 0
    checks_warned: int = 0
    issues: List[Dict[str, Any]] = Field(default_factory=list)


class ReviewReport(BaseModel):
    """AI review report."""
    analysis_method: str = "deterministic"
    readiness_score: float = 0.0
    readiness_label: str = "Not Reviewed"
    strengths: List[Dict[str, Any]] = Field(default_factory=list)
    weaknesses: List[Dict[str, Any]] = Field(default_factory=list)
    category_scores: Dict[str, float] = Field(default_factory=dict)
    improvement_suggestions: List[str] = Field(default_factory=list)


class FormattingReport(BaseModel):
    """Formatting status report."""
    template_id: Optional[str] = None
    status: str = "not_formatted"
    validation_score: float = 0.0
    output_path: Optional[str] = None


class ExportReport(BaseModel):
    """Export status report."""
    format: str = "docx"
    status: str = "not_exported"
    file_path: Optional[str] = None
    file_name: Optional[str] = None


# ─── Canonical Manuscript ─────────────────────────────────────────────────────


class StructuredManuscript(BaseModel):
    """Canonical Manuscript JSON — the single source of truth.

    Every module in the system reads from and writes to this model.
    Missing fields use forgiving defaults so old data still loads.
    """
    # Core content
    title: str = ""
    authors: List[Author] = Field(default_factory=list)
    affiliations: List[str] = Field(default_factory=list)
    abstract: str = ""
    keywords: List[str] = Field(default_factory=list)
    sections: List[ManuscriptSection] = Field(default_factory=list)
    references: List[Reference] = Field(default_factory=list)
    tables: List[Table] = Field(default_factory=list)
    figures: List[Figure] = Field(default_factory=list)

    # Counts
    word_count: int = 0
    section_count: int = 0
    reference_count: int = 0
    language: str = "en"

    # V2: Intelligence layers
    citation_map: CitationMap = Field(default_factory=CitationMap)
    doi_records: List[DOIRecord] = Field(default_factory=list)
    compliance_report: Optional[ComplianceReport] = None
    review_report: Optional[ReviewReport] = None
    formatting_report: Optional[FormattingReport] = None
    export_report: Optional[ExportReport] = None

    # Metadata
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_formatting_input(self) -> Dict[str, Any]:
        """Convert to the dict format expected by the formatting engine."""
        return {
            "title": self.title,
            "authors": [{"name": a.name, "affiliation": a.affiliation} for a in self.authors],
            "abstract": self.abstract,
            "keywords": self.keywords,
            "sections": [
                {
                    "heading": s.heading,
                    "label": s.label.value,
                    "content": s.content,
                    "level": s.level,
                    "tables": [t.model_dump() for t in s.tables],
                    "figures": [f.model_dump() for f in s.figures],
                }
                for s in self.sections
            ],
            "references": [
                {
                    "index": r.index,
                    "raw_text": r.raw_text,
                    "authors": r.authors,
                    "title": r.title,
                    "journal": r.journal,
                    "year": r.year,
                    "doi": r.doi,
                    "volume": r.volume,
                    "pages": r.pages,
                }
                for r in self.references
            ],
            "tables": [t.model_dump() for t in self.tables],
            "figures": [f.model_dump() for f in self.figures],
            "word_count": self.word_count,
            "metadata": self.metadata,
        }

    def compute_counts(self):
        """Recompute derived counts from content."""
        self.section_count = len(self.sections)
        self.reference_count = len(self.references)
        self.word_count = len(self.abstract.split()) if self.abstract else 0
        for sec in self.sections:
            self.word_count += len(sec.content.split())


# ─── Forgiving Deserializer ──────────────────────────────────────────────────


def manuscript_from_dict(data: Dict[str, Any]) -> StructuredManuscript:
    """Build a StructuredManuscript from any dict, forgiving missing/malformed fields.

    Handles:
    - Missing 'manuscript_model' key (builds from parsed_json)
    - Missing id/index fields
    - Figure strings instead of dicts
    - Missing authors list
    - V2: citation_map, doi_records, reports
    """
    if "title" in data:
        return _safe_parse(data)
    return _safe_parse(data.get("manuscript_model", data))


def _safe_parse(data: Dict[str, Any]) -> StructuredManuscript:
    """Parse with forgiving defaults for all known structural mismatches."""
    sections_raw = data.get("sections") or []
    sections = []
    for idx, sec in enumerate(sections_raw):
        if isinstance(sec, dict):
            fig_objs = []
            for f in sec.get("figures", []):
                if isinstance(f, str):
                    fig_objs.append(Figure(caption=f))
                elif isinstance(f, dict):
                    fig_objs.append(Figure(**f))
            sections.append(ManuscriptSection(
                id=sec.get("id", _new_id()),
                heading=sec.get("heading") or "",
                label=sec.get("label", "other"),
                content=sec.get("content") or "",
                level=sec.get("level", 1),
                confidence=sec.get("confidence", 0.0),
                tables=[Table(**t) if isinstance(t, dict) else Table() for t in (sec.get("tables") or [])],
                figures=fig_objs,
            ))

    refs_raw = data.get("references") or []
    references = []
    for i, ref in enumerate(refs_raw):
        if isinstance(ref, dict):
            ref.setdefault("index", i + 1)
            if ref.get("authors") is None:
                ref["authors"] = ref.get("authors") or []
            references.append(Reference(**ref))
        elif isinstance(ref, str):
            references.append(Reference(raw_text=ref, index=i + 1))

    tables_raw = data.get("tables") or []
    tables = [Table(**t) if isinstance(t, dict) else Table() for t in tables_raw]

    fig_objs = []
    for f in data.get("figures", []):
        if isinstance(f, str):
            fig_objs.append(Figure(caption=f))
        elif isinstance(f, dict):
            fig_objs.append(Figure(**f))

    authors_raw = data.get("authors") or []
    authors = []
    for a in authors_raw:
        if isinstance(a, dict):
            authors.append(Author(**a))
        elif isinstance(a, str):
            authors.append(Author(name=a))

    # V2: Parse citation_map
    citation_map_raw = data.get("citation_map")
    citation_map = CitationMap(**citation_map_raw) if isinstance(citation_map_raw, dict) else CitationMap()

    # V2: Parse doi_records
    doi_records_raw = data.get("doi_records") or []
    doi_records = [DOIRecord(**d) if isinstance(d, dict) else DOIRecord() for d in doi_records_raw]

    # V2: Parse reports
    compliance_raw = data.get("compliance_report")
    compliance_report = ComplianceReport(**compliance_raw) if isinstance(compliance_raw, dict) else None

    review_raw = data.get("review_report")
    review_report = ReviewReport(**review_raw) if isinstance(review_raw, dict) else None

    formatting_raw = data.get("formatting_report")
    formatting_report = FormattingReport(**formatting_raw) if isinstance(formatting_raw, dict) else None

    export_raw = data.get("export_report")
    export_report = ExportReport(**export_raw) if isinstance(export_raw, dict) else None

    ms = StructuredManuscript(
        title=data.get("title") or "",
        authors=authors,
        affiliations=data.get("affiliations") or [],
        abstract=data.get("abstract") or "",
        keywords=data.get("keywords") or [],
        sections=sections,
        references=references,
        tables=tables,
        figures=fig_objs,
        word_count=data.get("word_count", 0) or 0,
        section_count=len(sections),
        reference_count=len(references),
        language=data.get("language", "en"),
        citation_map=citation_map,
        doi_records=doi_records,
        compliance_report=compliance_report,
        review_report=review_report,
        formatting_report=formatting_report,
        export_report=export_report,
        metadata=data.get("metadata") or {},
    )
    ms.compute_counts()
    return ms
