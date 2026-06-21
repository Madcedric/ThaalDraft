"""Markdown Extractor — V2 with enhanced parsing."""

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


class MarkdownExtractor(BaseExtractor):
    """Extract structured content from Markdown files."""

    @property
    def supported_extensions(self) -> list[str]:
        return [".md"]

    def extract(self, file_path: str) -> ExtractionResult:
        start = time.time()
        result = ExtractionResult()
        result.metadata = ExtractionMetadata(
            file_type="markdown",
            file_size_bytes=os.path.getsize(file_path),
            parser_used="markdown_extractor_v2",
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
            result.metadata.warnings.append(f"Markdown extraction error: {str(e)}")

        result.metadata.processing_time_ms = (time.time() - start) * 1000
        return result

    def _extract_title(self, content: str, result: ExtractionResult):
        match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        if match:
            result.title = match.group(1).strip()

    def _extract_authors(self, content: str, result: ExtractionResult):
        match = re.search(r"^(?:by|author[s]?:?)\s*(.+)$", content, re.IGNORECASE | re.MULTILINE)
        if match:
            author_text = match.group(1).strip()
            result.authors = [a.strip() for a in author_text.split(" and ")]

    def _extract_abstract(self, content: str, result: ExtractionResult):
        # Try blockquote abstract
        match = re.search(
            r"(?:^>?\s*abstract:?\s*$|^\*\*abstract\*\*:?\s*$)(.*?)(?=^#|\Z)",
            content, re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        if match:
            result.abstract = re.sub(r"^>?\s*", "", match.group(1), flags=re.MULTILINE)
            result.abstract = re.sub(r"\n\s*\n", "\n", result.abstract).strip()
            return

        # Try frontmatter abstract
        frontmatter = re.search(r"^---+\s*\n(.*?)\n---+", content, re.DOTALL)
        if frontmatter:
            abs_match = re.search(r"abstract:\s*(.+?)(?:\n|\Z)", frontmatter.group(1), re.IGNORECASE)
            if abs_match:
                result.abstract = abs_match.group(1).strip()

    def _extract_figures(self, content: str, result: ExtractionResult):
        for match in re.finditer(r"!\[([^\]]*)\]\(([^)]+)\)", content):
            caption = match.group(1) or "Figure"
            path = match.group(2)
            result.figures.append(ExtractedFigure(caption=caption, path=path))

    def _extract_tables(self, content: str, result: ExtractionResult):
        table_lines = []
        in_table = False
        table_order = 0
        for line in content.split("\n"):
            if re.match(r"^\|[-:\s|]+\|$", line):
                continue
            if re.match(r"^\|", line):
                in_table = True
                cells = [c.strip() for c in line.split("|")[1:-1]]
                table_lines.append(cells)
            else:
                if in_table and table_lines:
                    table_order += 1
                    result.tables.append(ExtractedTable(
                        caption=f"Table {table_order}",
                        rows=table_lines,
                        order=table_order,
                    ))
                    table_lines = []
                    in_table = False
        if table_lines:
            table_order += 1
            result.tables.append(ExtractedTable(
                caption=f"Table {table_order}",
                rows=table_lines,
                order=table_order,
            ))

    def _extract_references(self, content: str, result: ExtractionResult):
        # Try explicit references section
        ref_match = re.search(
            r"(?:^#+\s*(?:references|bibliography|works cited)\s*$)(.*?)(?=\Z)",
            content, re.IGNORECASE | re.MULTILINE | re.DOTALL,
        )
        if ref_match:
            ref_text = ref_match.group(1).strip()
            ref_items = re.findall(r"(?:\d+\.\s+|\*\s+|\-\s+)(.+)", ref_text)
            for i, r in enumerate(ref_items):
                if r.strip():
                    doi_match = re.search(r"10\.\d{4,}/[^\s\)\],;]+", r)
                    doi = doi_match.group(0).rstrip(".,;)") if doi_match else None
                    result.references.append(ExtractedReference(
                        raw_text=r.strip(),
                        index=i + 1,
                        doi=doi,
                    ))

    def _extract_sections(self, content: str, result: ExtractionResult):
        heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)
        heading_positions = [
            (m.start(), len(m.group(1)), m.group(2))
            for m in heading_pattern.finditer(content)
        ]

        # Build clean text body
        text_body = re.sub(r"^---+.*?---+", "", content, flags=re.DOTALL)
        text_body = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", text_body)
        text_body = re.sub(r"\[([^\]]+)\]\([^)]*\)", r"\1", text_body)
        text_body = re.sub(r"[*_`~]", "", text_body)

        if heading_positions:
            for i, (pos, level, heading) in enumerate(heading_positions):
                if i + 1 < len(heading_positions):
                    next_pos = heading_positions[i + 1][0]
                    section_text = text_body[pos:next_pos]
                else:
                    section_text = text_body[pos:]

                section_text = re.sub(r"\s+", " ", section_text).strip()
                section_text = re.sub(r"^#{1,6}\s+.+?", "", section_text).strip()

                if level <= 2:
                    result.sections.append(ExtractedSection(
                        heading=heading,
                        content=section_text,
                        level=level,
                        order=i + 1,
                    ))
                else:
                    if result.sections:
                        result.sections[-1].content += " " + section_text
        else:
            result.sections.append(ExtractedSection(
                heading="",
                content=text_body.strip()[:5000],
                order=1,
            ))
