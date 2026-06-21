"""LaTeX Extractor — V2 with enhanced parsing."""

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


class LaTeXExtractor(BaseExtractor):
    """Extract structured content from LaTeX files."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".tex"]

    def extract(self, file_path: str) -> ExtractionResult:
        start = time.time()
        result = ExtractionResult()
        result.metadata = ExtractionMetadata(
            file_type="latex",
            file_size_bytes=os.path.getsize(file_path),
            parser_used="latex_extractor_v2",
        )

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()

            result.raw_text = content
            self._extract_title(content, result)
            self._extract_authors(content, result)
            self._extract_abstract(content, result)
            self._extract_figures(content, result)
            self._extract_tables(content, result)
            self._extract_references(content, result)
            self._extract_sections(content, result)

        except Exception as e:
            result.metadata.warnings.append(f"LaTeX extraction error: {str(e)}")

        result.metadata.processing_time_ms = (time.time() - start) * 1000
        return result

    def _clean_latex(self, text: str) -> str:
        """Remove LaTeX commands from text."""
        cleaned = re.sub(r"\\[a-zA-Z]+(\{[^}]*\}|\[[^\]]*\])?", "", text)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned

    def _extract_title(self, content: str, result: ExtractionResult):
        match = re.search(r"\\title\{([^}]+)\}", content)
        if match:
            result.title = self._clean_latex(match.group(1))

    def _extract_authors(self, content: str, result: ExtractionResult):
        author_matches = re.findall(r"\\author\{([^}]+)\}", content)
        if author_matches:
            for author_str in author_matches:
                author_str = author_str.strip()
                if "\\" not in author_str:
                    result.authors.extend([a.strip() for a in author_str.split(" and ")])
                else:
                    clean = self._clean_latex(author_str)
                    if clean:
                        result.authors.extend([a.strip() for a in clean.split(" and ")])

    def _extract_abstract(self, content: str, result: ExtractionResult):
        match = re.search(r"\\begin\{abstract\}(.*?)\\end\{abstract\}", content, re.DOTALL)
        if match:
            result.abstract = self._clean_latex(match.group(1))

    def _extract_figures(self, content: str, result: ExtractionResult):
        fig_pattern = re.compile(
            r"\\begin\{figure\*?\}(.*?)\\end\{figure\*?\}",
            re.DOTALL,
        )
        for i, match in enumerate(fig_pattern.finditer(content)):
            fig_content = match.group(1)
            caption_match = re.search(r"\\caption\{([^}]+)\}", fig_content)
            caption = caption_match.group(1) if caption_match else f"Figure {i + 1}"
            result.figures.append(ExtractedFigure(
                caption=self._clean_latex(caption),
                order=i + 1,
            ))

    def _extract_tables(self, content: str, result: ExtractionResult):
        table_pattern = re.compile(
            r"\\begin\{table\*?\}(.*?)\\end\{table\*?\}",
            re.DOTALL,
        )
        for i, match in enumerate(table_pattern.finditer(content)):
            tbl_content = match.group(1)
            caption_match = re.search(r"\\caption\{([^}]+)\}", tbl_content)
            caption = caption_match.group(1) if caption_match else f"Table {i + 1}"

            # Extract tabular data
            rows = []
            tabular_match = re.search(r"\\begin\{tabular\}.*?\n(.*?)\\end\{tabular\}", tbl_content, re.DOTALL)
            if tabular_match:
                for line in tabular_match.group(1).split("\n"):
                    line = line.strip()
                    if line and not line.startswith("\\") and "&" in line:
                        cells = [self._clean_latex(c) for c in line.split("&")]
                        rows.append(cells)

            result.tables.append(ExtractedTable(
                caption=self._clean_latex(caption),
                rows=rows,
                order=i + 1,
            ))

    def _extract_references(self, content: str, result: ExtractionResult):
        # thebibliography environment
        bib_match = re.search(r"\\begin\{thebibliography\}(.*?)\\end\{thebibliography\}", content, re.DOTALL)
        if bib_match:
            bib_items = re.findall(r"\\bibitem\{[^}]*\}(.*?)(?=\\bibitem|\Z)", bib_match.group(1), re.DOTALL)
            for i, item in enumerate(bib_items):
                clean_item = self._clean_latex(item)
                if clean_item:
                    doi_match = re.search(r"10\.\d{4,}/[^\s\)\],;]+", clean_item)
                    doi = doi_match.group(0).rstrip(".,;)") if doi_match else None
                    result.references.append(ExtractedReference(
                        raw_text=clean_item,
                        index=i + 1,
                        doi=doi,
                    ))

        # \bibliography command (external .bib file)
        if not result.references:
            biblio_match = re.search(r"\\bibliography\{([^}]+)\}", content)
            if biblio_match:
                result.references.append(ExtractedReference(
                    raw_text=f"Bibliography file: {biblio_match.group(1)}",
                    index=1,
                ))

    def _extract_sections(self, content: str, result: ExtractionResult):
        section_pattern = re.compile(r"\\section\*?\{([^}]+)\}")
        subsection_pattern = re.compile(r"\\subsection\*?\{([^}]+)\}")

        section_positions = [(m.start(), m.group(1), "section") for m in section_pattern.finditer(content)]
        subsection_positions = [(m.start(), m.group(1), "subsection") for m in subsection_pattern.finditer(content)]
        all_positions = sorted(section_positions + subsection_positions, key=lambda x: x[0])

        text_body = self._clean_latex(content)

        if all_positions:
            for i, (pos, heading, level) in enumerate(all_positions):
                if i + 1 < len(all_positions):
                    next_pos = all_positions[i + 1][0]
                    section_text = text_body[pos:next_pos]
                else:
                    section_text = text_body[pos:]

                section_text = self._clean_latex(section_text)

                if level == "section":
                    result.sections.append(ExtractedSection(
                        heading=heading,
                        content=section_text,
                        level=1,
                        order=i + 1,
                    ))
                else:
                    if result.sections:
                        result.sections[-1].content += " " + section_text
        else:
            result.sections.append(ExtractedSection(
                heading="",
                content=text_body[:5000],
                order=1,
            ))
