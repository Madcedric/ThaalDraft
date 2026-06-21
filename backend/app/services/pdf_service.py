import os
import shutil
import subprocess
from typing import Optional


def convert_docx_to_pdf_docx2pdf(input_path: str, output_path: str) -> bool:
    try:
        # Try using docx2pdf if available (works on Windows and macOS)
        from docx2pdf import convert
        convert(input_path, output_path)
        return os.path.exists(output_path)
    except Exception:
        return False


def convert_docx_to_pdf_libreoffice(input_path: str, output_path: str) -> bool:
    try:
        # Use libreoffice in headless mode to convert
        # libreoffice --headless --convert-to pdf --outdir <outdir> <input>
        outdir = os.path.dirname(output_path) or "."
        cmd = [
            "libreoffice",
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            outdir,
            input_path,
        ]
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=120)
        # LibreOffice writes to outdir with same base name
        base = os.path.splitext(os.path.basename(input_path))[0]
        produced = os.path.join(outdir, f"{base}.pdf")
        if os.path.exists(produced):
            # Move/rename to requested output path
            if produced != output_path:
                shutil.move(produced, output_path)
            return True
        return False
    except Exception:
        return False


def convert_docx_to_pdf(input_path: str, output_path: str) -> bool:
    """Attempt to convert DOCX to PDF using available tools.

    Returns True on success, False otherwise.
    """
    # Try docx2pdf first (Python wrapper)
    if convert_docx_to_pdf_docx2pdf(input_path, output_path):
        return True

    # Next try LibreOffice
    if convert_docx_to_pdf_libreoffice(input_path, output_path):
        return True

    # Could add pandoc or other tools later
    return False
