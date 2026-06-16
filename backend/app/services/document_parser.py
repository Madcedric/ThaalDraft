import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException

UPLOAD_DIR = "uploads"
ALLOWED_EXTENSIONS = {".docx", ".pdf", ".tex", ".md"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

MIME_TYPE_MAP = {
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
    ".tex": "application/x-latex",
    ".md": "text/markdown",
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
            detail=f"Invalid file type '{ext}'. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
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
    """Parse a document based on its file extension."""
    ext = get_file_extension(file_path)
    
    if ext == ".docx":
        from app.services.docx_parser import parse_docx
        return parse_docx(file_path)
    elif ext == ".pdf":
        from app.services.pdf_parser import parse_pdf
        return parse_pdf(file_path)
    elif ext == ".tex":
        from app.services.latex_parser import parse_latex
        return parse_latex(file_path)
    elif ext == ".md":
        from app.services.markdown_parser import parse_markdown
        return parse_markdown(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")


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
