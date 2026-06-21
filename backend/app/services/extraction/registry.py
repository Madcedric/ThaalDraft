"""Extractor Registry — maps file extensions to extractors."""

import os
from typing import Dict, Optional

from app.services.extraction.base import BaseExtractor
from app.services.extraction.report import ExtractionResult
from app.services.extraction.docx_extractor import DOCXExtractor
from app.services.extraction.pdf_extractor import PDFExtractor
from app.services.extraction.markdown_extractor import MarkdownExtractor
from app.services.extraction.latex_extractor import LaTeXExtractor
from app.services.extraction.text_extractor import TextExtractor

# Registry of extractors by extension
_EXTRACTORS: Dict[str, BaseExtractor] = {}

def _build_registry():
    """Build the extractor registry."""
    global _EXTRACTORS
    if _EXTRACTORS:
        return

    extractors = [
        DOCXExtractor(),
        PDFExtractor(),
        MarkdownExtractor(),
        LaTeXExtractor(),
        TextExtractor(),
    ]

    for extractor in extractors:
        for ext in extractor.supported_extensions:
            _EXTRACTORS[ext] = extractor


def get_extractor(file_path: str) -> Optional[BaseExtractor]:
    """Get the appropriate extractor for a file."""
    _build_registry()
    ext = os.path.splitext(file_path)[1].lower()
    return _EXTRACTORS.get(ext)


def extract_document(file_path: str) -> ExtractionResult:
    """Extract structured content from a document file.

    This is the main entry point for the Document Intelligence Layer.
    It dispatches to the appropriate extractor based on file extension.

    Args:
        file_path: Path to the document file.

    Returns:
        ExtractionResult with all extracted content and metadata.
    """
    _build_registry()
    ext = os.path.splitext(file_path)[1].lower()
    extractor = _EXTRACTORS.get(ext)

    if not extractor:
        supported = ", ".join(sorted(_EXTRACTORS.keys()))
        return ExtractionResult(
            metadata=__import__("app.services.extraction.report", fromlist=["ExtractionMetadata"]).ExtractionMetadata(
                file_type=ext or "unknown",
                parser_used="none",
                warnings=[f"Unsupported file format: {ext}. Supported: {supported}"],
            )
        )

    return extractor.extract(file_path)


def get_supported_extensions() -> list[str]:
    """Return all supported file extensions."""
    _build_registry()
    return sorted(_EXTRACTORS.keys())
