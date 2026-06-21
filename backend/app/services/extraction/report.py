"""Extraction report models — standardized output from all extractors."""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import time


@dataclass
class ExtractedSection:
    """A single extracted section."""
    heading: str
    content: str
    level: int = 1
    order: int = 0


@dataclass
class ExtractedFigure:
    """A single extracted figure."""
    caption: str
    path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    mime_type: Optional[str] = None


@dataclass
class ExtractedTable:
    """A single extracted table."""
    caption: Optional[str] = None
    rows: List[List[str]] = field(default_factory=list)
    order: int = 0


@dataclass
class ExtractedReference:
    """A single extracted reference."""
    raw_text: str
    index: int = 0
    doi: Optional[str] = None


@dataclass
class ExtractionMetadata:
    """Metadata about the extraction process."""
    file_type: str
    file_size_bytes: int = 0
    parser_used: str = ""
    processing_time_ms: float = 0
    page_count: Optional[int] = None
    has_images: bool = False
    has_tables: bool = False
    is_scanned_pdf: bool = False
    ocr_used: bool = False
    styles_extracted: bool = False
    warnings: List[str] = field(default_factory=list)


@dataclass
class ExtractionResult:
    """Standardized output from all document extractors."""
    title: str = ""
    authors: List[str] = field(default_factory=list)
    affiliations: List[str] = field(default_factory=list)
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    sections: List[ExtractedSection] = field(default_factory=list)
    references: List[ExtractedReference] = field(default_factory=list)
    figures: List[ExtractedFigure] = field(default_factory=list)
    tables: List[ExtractedTable] = field(default_factory=list)
    metadata: ExtractionMetadata = field(default_factory=lambda: ExtractionMetadata(file_type="unknown"))
    raw_text: str = ""

    @property
    def word_count(self) -> int:
        """Count words across all sections + abstract."""
        count = len(self.abstract.split()) if self.abstract else 0
        for sec in self.sections:
            count += len(sec.content.split())
        return count

    @property
    def section_count(self) -> int:
        return len(self.sections)

    @property
    def reference_count(self) -> int:
        return len(self.references)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "title": self.title,
            "authors": self.authors,
            "affiliations": self.affiliations,
            "abstract": self.abstract,
            "keywords": self.keywords,
            "sections": [
                {"heading": s.heading, "content": s.content, "level": s.level, "order": s.order}
                for s in self.sections
            ],
            "references": [
                {"raw_text": r.raw_text, "index": r.index, "doi": r.doi}
                for r in self.references
            ],
            "figures": [
                {"caption": f.caption, "path": f.path, "width": f.width, "height": f.height, "mime_type": f.mime_type}
                for f in self.figures
            ],
            "tables": [
                {"caption": t.caption, "rows": t.rows, "order": t.order}
                for t in self.tables
            ],
            "metadata": {
                "file_type": self.metadata.file_type,
                "file_size_bytes": self.metadata.file_size_bytes,
                "parser_used": self.metadata.parser_used,
                "processing_time_ms": self.metadata.processing_time_ms,
                "page_count": self.metadata.page_count,
                "has_images": self.metadata.has_images,
                "has_tables": self.metadata.has_tables,
                "is_scanned_pdf": self.metadata.is_scanned_pdf,
                "ocr_used": self.metadata.ocr_used,
                "styles_extracted": self.metadata.styles_extracted,
                "warnings": self.metadata.warnings,
            },
            "raw_text": self.raw_text,
            "word_count": self.word_count,
            "section_count": self.section_count,
            "reference_count": self.reference_count,
        }
