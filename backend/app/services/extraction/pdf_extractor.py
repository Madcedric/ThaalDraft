"""PDF Extractor — V2 with PyMuPDF + pdfplumber + OCR fallback.

Extracts text, headings, tables, figures, and metadata from PDF files.
Falls back to OCR (EasyOCR) for scanned PDFs with < 100 chars of text.
"""

import os
import re
import time
from typing import List, Optional

from app.services.extraction.base import BaseExtractor
from app.services.extraction.report import (
    ExtractionResult,
    ExtractionMetadata,
    ExtractedSection,
    ExtractedFigure,
    ExtractedTable,
    ExtractedReference,
)


HEADING_LABELS = {
    "abstract": "abstract",
    "introduction": "introduction",
    "related work": "related_work",
    "literature review": "related_work",
    "methodology": "methodology",
    "methods": "methods",
    "method": "methods",
    "proposed method": "methods",
    "proposed approach": "methods",
    "experiments": "experiments",
    "experimental setup": "experiments",
    "evaluation": "experiments",
    "results": "results",
    "results and discussion": "discussion",
    "discussion": "discussion",
    "conclusion": "conclusion",
    "conclusions": "conclusion",
    "acknowledgments": "acknowledgments",
    "acknowledgements": "acknowledgments",
    "references": "references",
    "bibliography": "references",
    "appendix": "appendix",
}


def _classify_heading(text: str) -> str:
    norm = text.lower().strip()
    for key, label in HEADING_LABELS.items():
        if key in norm or norm in key:
            return label
    return "other"


class PDFExtractor(BaseExtractor):
    """Extract structured content from PDF files."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".pdf"]

    def extract(self, file_path: str) -> ExtractionResult:
        start = time.time()
        result = ExtractionResult()
        result.metadata = ExtractionMetadata(
            file_type="pdf",
            file_size_bytes=os.path.getsize(file_path),
            parser_used="pdf_extractor_v2",
        )

        try:
            self._extract_with_pymupdf(file_path, result)

            # Check if text extraction was insufficient → try OCR
            if len(result.raw_text.strip()) < 100:
                result.metadata.is_scanned_pdf = True
                result.metadata.warnings.append("Low text yield, attempting OCR fallback")
                self._extract_with_ocr(file_path, result)

            # Try pdfplumber for table extraction
            self._extract_tables_with_pdfplumber(file_path, result)

        except Exception as e:
            result.metadata.warnings.append(f"PDF extraction error: {str(e)}")

        result.metadata.processing_time_ms = (time.time() - start) * 1000
        return result

    def _extract_with_pymupdf(self, file_path: str, result: ExtractionResult):
        """Primary extraction using PyMuPDF."""
        try:
            import fitz
        except ImportError:
            result.metadata.warnings.append("PyMuPDF not installed")
            return

        doc = fitz.open(file_path)
        result.metadata.page_count = len(doc)

        full_text = ""
        heading_pattern = re.compile(r"^(\d+\.?\s+|[A-Z][A-Z\s]{2,})$")
        abstract_pattern = re.compile(r"^(abstract|summary)$", re.IGNORECASE)
        reference_pattern = re.compile(r"^(references|bibliography|works cited)$", re.IGNORECASE)
        figure_pattern = re.compile(r"^(fig\.|figure)\s*\d+[:\.\-]", re.IGNORECASE)
        author_pattern = re.compile(
            r"^(?:by\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)*)",
            re.IGNORECASE,
        )

        current_section = "general"
        current_heading = ""
        title = ""
        authors = []
        abstract = ""
        sections: List[ExtractedSection] = []
        references: List[ExtractedReference] = []
        figures: List[ExtractedFigure] = []
        section_order = 0
        ref_index = 0

        for page_num in range(len(doc)):
            page = doc.load_page(page_num)
            text = page.get_text()
            full_text += text + "\n"

            lines = text.split("\n")
            for line in lines:
                line = line.strip()
                if not line:
                    continue

                # Title (first substantial non-numbered line)
                if not title and len(line) < 150 and not line.startswith(("1.", "2.", "3.", "I.", "II.", "III")):
                    title = line
                    continue

                # Authors
                if not authors and author_pattern.match(line) and len(line) < 200:
                    author_text = line.replace("by ", "", 1) if line.lower().startswith("by ") else line
                    authors = [a.strip() for a in author_text.split(",")]
                    continue

                # Abstract
                if abstract_pattern.match(line):
                    current_section = "abstract"
                    continue

                # References
                if reference_pattern.match(line):
                    current_section = "references"
                    continue

                # Headings
                if heading_pattern.match(line) and len(line) < 100:
                    current_section = "body"
                    current_heading = line
                    section_order += 1
                    sections.append(ExtractedSection(
                        heading=current_heading,
                        content="",
                        order=section_order,
                    ))
                    continue

                # Figures
                if figure_pattern.match(line):
                    figures.append(ExtractedFigure(caption=line))
                    continue

                # Content routing
                if current_section == "abstract":
                    abstract += line + "\n"
                elif current_section == "references":
                    ref_index += 1
                    doi_match = re.search(r"10\.\d{4,}/[^\s\)\],;]+", line)
                    doi = doi_match.group(0).rstrip(".,;)") if doi_match else None
                    references.append(ExtractedReference(
                        raw_text=line,
                        index=ref_index,
                        doi=doi,
                    ))
                elif current_section == "body":
                    if sections:
                        sections[-1].content += line + "\n"
                    else:
                        section_order += 1
                        sections.append(ExtractedSection(
                            heading="",
                            content=line + "\n",
                            order=section_order,
                        ))
                else:
                    if sections:
                        sections[-1].content += line + "\n"
                    else:
                        section_order += 1
                        sections.append(ExtractedSection(
                            heading="",
                            content=line + "\n",
                            order=section_order,
                        ))
                        current_section = "body"

        doc.close()

        result.title = title
        result.authors = authors
        result.abstract = abstract.strip()
        result.sections = sections
        result.references = references
        result.figures = figures
        result.raw_text = full_text

    def _extract_tables_with_pdfplumber(self, file_path: str, result: ExtractionResult):
        """Try to extract tables using pdfplumber."""
        try:
            import pdfplumber
        except ImportError:
            return

        try:
            with pdfplumber.open(file_path) as pdf:
                table_count = 0
                for page in pdf.pages:
                    page_tables = page.extract_tables()
                    for table_data in page_tables:
                        if table_data and len(table_data) > 1:
                            table_count += 1
                            caption = f"Table {table_count}"
                            rows = []
                            for row in table_data:
                                rows.append([str(cell) if cell else "" for cell in row])
                            result.tables.append(ExtractedTable(
                                caption=caption,
                                rows=rows,
                                order=table_count,
                            ))
                result.metadata.has_tables = len(result.tables) > 0
        except Exception:
            pass

    def _extract_with_ocr(self, file_path: str, result: ExtractionResult):
        """Fallback OCR extraction for scanned PDFs."""
        try:
            from app.services.ocr_service import extract_text_from_pdf
            ocr_text = extract_text_from_pdf(file_path)
            if ocr_text and len(ocr_text) > len(result.raw_text):
                result.raw_text = ocr_text
                result.metadata.ocr_used = True

                # Parse OCR text into sections
                lines = ocr_text.split("\n")
                current_heading = ""
                section_order = len(result.sections)
                for line in lines:
                    line = line.strip()
                    if not line:
                        continue
                    if len(line) < 100 and line.isupper():
                        section_order += 1
                        current_heading = line
                        result.sections.append(ExtractedSection(
                            heading=current_heading,
                            content="",
                            order=section_order,
                        ))
                    elif result.sections:
                        result.sections[-1].content += line + "\n"
        except Exception as e:
            result.metadata.warnings.append(f"OCR fallback failed: {str(e)}")
