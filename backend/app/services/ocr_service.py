"""OCR Support Module.

Extracts text from scanned PDFs and images using EasyOCR.
Falls back to PyMuPDF text extraction for non-scanned documents.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

_ocr_reader = None


def _get_ocr_reader():
    global _ocr_reader
    if _ocr_reader is None:
        try:
            import easyocr
            _ocr_reader = easyocr.Reader(["en"], gpu=False)
            logger.info("EasyOCR initialized (CPU mode)")
        except Exception as e:
            logger.warning(f"EasyOCR init failed: {e}")
    return _ocr_reader


def ocr_image(image_path: str) -> str:
    """Extract text from an image file using EasyOCR."""
    reader = _get_ocr_reader()
    if not reader:
        return ""

    try:
        results = reader.readtext(image_path, detail=0)
        return "\n".join(results)
    except Exception as e:
        logger.warning(f"OCR failed for {image_path}: {e}")
        return ""


def ocr_pdf_page(pdf_path: str, page_num: int = 0) -> str:
    """Extract text from a single PDF page using OCR."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        if page_num >= len(doc):
            return ""

        page = doc[page_num]
        pix = page.get_pixmap(dpi=200)
        temp_path = f"_ocr_page_{page_num}.png"
        pix.save(temp_path)
        doc.close()

        text = ocr_image(temp_path)

        try:
            os.remove(temp_path)
        except OSError:
            pass

        return text
    except Exception as e:
        logger.warning(f"PDF OCR failed for page {page_num}: {e}")
        return ""


def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from a PDF. Tries PyMuPDF first, falls back to OCR."""
    try:
        import fitz
        doc = fitz.open(pdf_path)
        text_parts = []
        for page in doc:
            text = page.get_text()
            if text.strip():
                text_parts.append(text)

        doc.close()
        full_text = "\n".join(text_parts)

        if len(full_text.strip()) < 100:
            logger.info("PDF has minimal text, attempting OCR...")
            doc = fitz.open(pdf_path)
            ocr_parts = []
            for i, page in enumerate(doc):
                pix = page.get_pixmap(dpi=200)
                temp_path = f"_ocr_page_{i}.png"
                pix.save(temp_path)
                ocr_text = ocr_image(temp_path)
                if ocr_text:
                    ocr_parts.append(ocr_text)
                try:
                    os.remove(temp_path)
                except OSError:
                    pass
            doc.close()
            if ocr_parts:
                full_text = "\n".join(ocr_parts)

        return full_text
    except Exception as e:
        logger.warning(f"PDF extraction failed: {e}")
        return ""


def extract_text_from_image(image_path: str) -> str:
    """Extract text from an image file using OCR."""
    return ocr_image(image_path)
