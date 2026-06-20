"""Export Engine.

Generates DOCX and PDF files from StructuredManuscript.
"""
import os
import logging
from typing import Optional

from app.services.manuscript.model import StructuredManuscript
from app.services.formatting.engine_v2 import format_manuscript, TEMPLATE_CONFIGS

logger = logging.getLogger(__name__)


def export_docx(
    manuscript: StructuredManuscript,
    template_id: str = "ieee",
    output_dir: str = "exports",
    filename: Optional[str] = None,
) -> str:
    """Export manuscript as DOCX. Returns file path."""
    path = format_manuscript(manuscript, template_id, output_dir)
    if filename:
        new_path = os.path.join(output_dir, filename)
        os.rename(path, new_path)
        return new_path
    return path


def export_pdf(
    manuscript: StructuredManuscript,
    template_id: str = "ieee",
    output_dir: str = "exports",
    filename: Optional[str] = None,
) -> Optional[str]:
    """Export manuscript as PDF. Returns file path or None if conversion fails."""
    docx_path = export_docx(manuscript, template_id, output_dir)

    pdf_path = os.path.join(output_dir, filename or f"{template_id}_manuscript.pdf")

    try:
        from app.services.pdf_service import convert_docx_to_pdf
        if convert_docx_to_pdf(docx_path, pdf_path):
            return pdf_path
    except Exception as e:
        logger.warning(f"PDF conversion failed: {e}")

    return None


def get_supported_templates():
    """Return list of supported template IDs."""
    return list(TEMPLATE_CONFIGS.keys())
