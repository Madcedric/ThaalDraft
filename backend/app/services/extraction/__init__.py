"""Document Intelligence Layer — V2 extraction module.

Provides structured extraction from DOCX, PDF, Markdown, LaTeX, and TXT files.
Each extractor produces a standardized ExtractionResult.
"""

from app.services.extraction.report import ExtractionResult, ExtractionMetadata
from app.services.extraction.registry import get_extractor, extract_document

__all__ = [
    "ExtractionResult",
    "ExtractionMetadata",
    "get_extractor",
    "extract_document",
]
