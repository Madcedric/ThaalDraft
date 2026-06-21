"""Document Parser — V2 dispatcher.

Routes files to the appropriate V2 extractor from the extraction module.
Provides backward-compatible parse_document() interface.
"""

import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".docx", ".pdf", ".tex", ".md", ".txt"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

MIME_TYPE_MAP = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
    ".tex": "application/x-latex",
    ".md": "text/markdown",
    ".txt": "text/plain",
}

os.makedirs(UPLOAD_DIR, exist_ok=True)


def get_file_extension(filename: str) -> str:
    """Extract file extension from filename."""
    _, ext = os.path.splitext(filename)
    return ext.lower()


def validate_file(filename: str, file_size: int) -> str:
    """Validate file type and size. Returns the extension."""
    ext = get_file_extension(filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )
    if file_size > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024 * 1024)}MB"
        )
    return ext


async def save_upload_file(upload_file: UploadFile) -> str:
    """Saves the uploaded file locally and returns the file path."""
    content = await upload_file.read()
    file_size = len(content)

    ext = validate_file(upload_file.filename or "unknown", file_size)

    file_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{upload_file.filename}")

    with open(file_path, "wb") as buffer:
        buffer.write(content)

    return file_path


def parse_document(file_path: str) -> dict:
    """Parse a document using the V2 extraction module.

    Returns a backward-compatible dict with keys:
    title, authors, abstract, sections, references, tables, figures
    """
    from app.services.extraction.registry import extract_document

    result = extract_document(file_path)

    # Convert to backward-compatible dict
    return {
        "title": result.title,
        "authors": result.authors,
        "abstract": result.abstract,
        "sections": [
            {"heading": s.heading, "content": s.content}
            for s in result.sections
        ],
        "references": [r.raw_text for r in result.references],
        "tables": [t.rows for t in result.tables],
        "figures": [f.caption for f in result.figures],
        # V2 metadata
        "extraction_result": result.to_dict(),
        "metadata": {
            "file_type": result.metadata.file_type,
            "parser_used": result.metadata.parser_used,
            "processing_time_ms": result.metadata.processing_time_ms,
            "page_count": result.metadata.page_count,
            "has_images": result.metadata.has_images,
            "has_tables": result.metadata.has_tables,
            "is_scanned_pdf": result.metadata.is_scanned_pdf,
            "ocr_used": result.metadata.ocr_used,
            "styles_extracted": result.metadata.styles_extracted,
            "warnings": result.metadata.warnings,
        },
    }


def extract_metadata(parsed: dict) -> dict:
    """Extract metadata from parsed document."""
    title = parsed.get("title", "")
    authors = parsed.get("authors", [])
    abstract = parsed.get("abstract", "")
    sections = parsed.get("sections", [])
    references = parsed.get("references", [])

    word_count = 0
    for section in sections:
        content = section.get("content", "")
        word_count += len(content.split())

    return {
        "title": title,
        "authors": authors,
        "abstract_length": len(abstract.split()),
        "section_count": len(sections),
        "reference_count": len(references),
        "word_count": word_count,
        "has_abstract": bool(abstract),
        "has_references": bool(references),
    }
