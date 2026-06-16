import re
from typing import Optional


def parse_markdown(file_path: str) -> dict:
    """Parses a Markdown file and extracts structured text."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        raise ValueError(f"Failed to read Markdown file: {e}")

    title = ""
    authors = []
    abstract = ""
    sections = []
    references = []
    figures_data = []
    tables_data = []

    current_section = "general"
    current_heading = ""

    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
    if title_match:
        title = title_match.group(1).strip()

    author_match = re.search(r'^(?:by|author[s]?:?)\s*(.+)$', content, re.IGNORECASE | re.MULTILINE)
    if author_match:
        author_text = author_match.group(1).strip()
        authors = [a.strip() for a in author_text.split(' and ')]

    abstract_match = re.search(r'(?:^>?\s*abstract:?\s*$|^\*\*abstract\*\*:?\s*$)(.*?)(?=^#|\Z)', content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if abstract_match:
        abstract = re.sub(r'^>?\s*', '', abstract_match.group(1), flags=re.MULTILINE)
        abstract = re.sub(r'\n\s*\n', '\n', abstract).strip()

    if not abstract:
        abstract_block = re.search(r'^---+\s*\n(.*?)\n---+', content, re.DOTALL)
        if abstract_block:
            meta = abstract_block.group(1)
            abs_match = re.search(r'abstract:\s*(.+?)(?:\n|\Z)', meta, re.IGNORECASE)
            if abs_match:
                abstract = abs_match.group(1).strip()

    figure_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    for match in figure_pattern.finditer(content):
        caption = match.group(1) or "Figure"
        figures_data.append(caption)

    table_lines = []
    in_table = False
    for line in content.split('\n'):
        if re.match(r'^\|[-:\s|]+\|$', line):
            continue
        if re.match(r'^\|', line):
            in_table = True
            cells = [c.strip() for c in line.split('|')[1:-1]]
            table_lines.append(cells)
        else:
            if in_table and table_lines:
                tables_data.append(table_lines)
                table_lines = []
                in_table = False
    if table_lines:
        tables_data.append(table_lines)

    heading_pattern = re.compile(r'^(#{1,6})\s+(.+)$', re.MULTILINE)
    heading_positions = [(m.start(), len(m.group(1)), m.group(2)) for m in heading_pattern.finditer(content)]

    ref_match = re.search(r'(?:^#+\s*(?:references|bibliography|works cited)\s*$)(.*?)(?=\Z)', content, re.IGNORECASE | re.MULTILINE | re.DOTALL)
    if ref_match:
        ref_text = ref_match.group(1).strip()
        ref_items = re.findall(r'(?:\d+\.\s+|\*\s+|\-\s+)(.+)', ref_text)
        references = [r.strip() for r in ref_items if r.strip()]

    if not references:
        cite_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        for match in cite_pattern.finditer(content):
            ref_text = match.group(1)
            if any(c.isdigit() for c in ref_text) or '@' in ref_text:
                references.append(ref_text)

    text_body = re.sub(r'^---+.*?---+', '', content, flags=re.DOTALL)
    text_body = re.sub(r'!\[[^\]]*\]\([^)]*\)', '', text_body)
    text_body = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', text_body)
    text_body = re.sub(r'[*_`~]', '', text_body)

    if heading_positions:
        for i, (pos, level, heading) in enumerate(heading_positions):
            if i + 1 < len(heading_positions):
                next_pos = heading_positions[i + 1][0]
                section_text = text_body[pos:next_pos]
            else:
                section_text = text_body[pos:]

            section_text = re.sub(r'\s+', ' ', section_text).strip()
            section_text = re.sub(r'^#{1,6}\s+.+?', '', section_text).strip()

            if level <= 2:
                current_section = "body"
                current_heading = heading
                sections.append({"heading": current_heading, "content": section_text})
            else:
                if sections:
                    sections[-1]["content"] += " " + section_text
    else:
        sections.append({"heading": "", "content": text_body.strip()[:5000]})

    return {
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "sections": sections,
        "references": references,
        "tables": tables_data,
        "figures": figures_data
    }
