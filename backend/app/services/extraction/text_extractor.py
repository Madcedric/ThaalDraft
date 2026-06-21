"""Plain Text Extractor — V2 new addition for .txt support."""

import os
import re
import time
from typing import List

from app.services.extraction.base import BaseExtractor
from app.services.extraction.report import (
    ExtractionResult,
    ExtractionMetadata,
    ExtractedSection,
    ExtractedFigure,
    ExtractedTable,
    ExtractedReference,
)


class TextExtractor(BaseExtractor):
    """Extract structured content from plain text files."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".txt"]

    def extract(self, file_path: str) -> ExtractionResult:
        start = time.time()
        result = ExtractionResult()
        result.metadata = ExtractionMetadata(
            file_type="text",
            file_size_bytes=os.path.getsize(file_path),
            parser_used="text_extractor_v2",
        )

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            result.raw_text = content
            self._extract_from_text(content, result)

        except Exception as e:
            result.metadata.warnings.append(f"Text extraction error: {str(e)}")

        result.metadata.processing_time_ms = (time.time() - start) * 1000
        return result

    def _extract_from_text(self, content: str, result: ExtractionResult):
        """Parse a plain text file into sections using heuristics."""
        lines = content.split("\n")

        # Heuristic patterns
        abstract_pattern = re.compile(r"^(abstract|summary)[:\s]*$", re.IGNORECASE)
        reference_pattern = re.compile(r"^(references|bibliography|works cited)[:\s]*$", re.IGNORECASE)
        heading_pattern = re.compile(r"^([A-Z][A-Z\s]{2,}|(?:\d+\.?\s+).+)$")
        figure_pattern = re.compile(r"^(fig\.|figure)\s*\d+[:\.\-]", re.IGNORECASE)

        title = ""
        authors = []
        abstract = ""
        sections: List[ExtractedSection] = []
        references: List[ExtractedReference] = []
        figures: List[ExtractedFigure] = []

        current_section = "general"
        section_order = 0
        ref_index = 0

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue

            # Title: first non-empty line if short
            if not title and len(stripped) < 150:
                title = stripped
                continue

            # Section markers
            if abstract_pattern.match(stripped):
                current_section = "abstract"
                continue
            if reference_pattern.match(stripped):
                current_section = "references"
                continue

            # Heading detection
            if heading_pattern.match(stripped) and len(stripped) < 100:
                current_section = "body"
                section_order += 1
                sections.append(ExtractedSection(
                    heading=stripped,
                    content="",
                    order=section_order,
                ))
                continue

            # Figure
            if figure_pattern.match(stripped):
                figures.append(ExtractedFigure(caption=stripped))
                continue

            # Content
            if current_section == "abstract":
                abstract += stripped + "\n"
            elif current_section == "references":
                ref_index += 1
                doi_match = re.search(r"10\.\d{4,}/[^\s\)\],;]+", stripped)
                doi = doi_match.group(0).rstrip(".,;)") if doi_match else None
                references.append(ExtractedReference(
                    raw_text=stripped,
                    index=ref_index,
                    doi=doi,
                ))
            else:
                if sections:
                    sections[-1].content += stripped + "\n"
                else:
                    section_order += 1
                    sections.append(ExtractedSection(
                        heading="",
                        content=stripped + "\n",
                        order=section_order,
                    ))
                    current_section = "body"

        result.title = title
        result.authors = authors
        result.abstract = abstract.strip()
        result.sections = sections
        result.references = references
        result.figures = figures
