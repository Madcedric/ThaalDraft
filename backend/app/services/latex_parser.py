import re
from typing import Optional


def parse_latex(file_path: str) -> dict:
    """Parses a LaTeX file and extracts structured text."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
    except Exception as e:
        raise ValueError(f"Failed to read LaTeX file: {e}")

    title = ""
    authors = []
    abstract = ""
    sections = []
    references = []
    figures_data = []
    tables_data = []

    current_section = "general"
    current_heading = ""

    title_match = re.search(r'\\title\{([^}]+)\}', content)
    if title_match:
        title = title_match.group(1).strip()

    author_matches = re.findall(r'\\author\{([^}]+)\}', content)
    if author_matches:
        for author_str in author_matches:
            author_str = author_str.strip()
            if '\\' not in author_str:
                authors.extend([a.strip() for a in author_str.split(' and ')])
            else:
                clean = re.sub(r'\\[a-zA-Z]+(\{[^}]*\}|\[[^\]]*\])?', '', author_str)
                clean = re.sub(r'\s+', ' ', clean).strip()
                if clean:
                    authors.extend([a.strip() for a in clean.split(' and ')])

    abstract_match = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', content, re.DOTALL)
    if abstract_match:
        abstract = re.sub(r'\\[a-zA-Z]+(\{[^}]*\}|\[[^\]]*\])?', '', abstract_match.group(1))
        abstract = re.sub(r'\s+', ' ', abstract).strip()

    section_pattern = re.compile(r'\\section\*?\{([^}]+)\}')
    subsection_pattern = re.compile(r'\\subsection\*?\{([^}]+)\}')

    cleaned_content = re.sub(r'\\begin\{(figure|table)\*?\}(.*?)\\end\{(figure|table)\*?\}', 
                             lambda m: figures_data.append(m.group(0)) if m.group(1) == 'figure' else tables_data.append(m.group(0)), 
                             content, flags=re.DOTALL)

    bib_match = re.search(r'\\begin\{thebibliography\}(.*?)\\end\{thebibliography\}', content, re.DOTALL)
    if bib_match:
        bib_items = re.findall(r'\\bibitem\{[^}]*\}(.*?)(?=\\bibitem|\Z)', bib_match.group(1), re.DOTALL)
        for item in bib_items:
            clean_item = re.sub(r'\\[a-zA-Z]+(\{[^}]*\}|\[[^\]]*\])?', '', item)
            clean_item = re.sub(r'\s+', ' ', clean_item).strip()
            if clean_item:
                references.append(clean_item)

    if not references:
        biblio_match = re.search(r'\\bibliography\{([^}]+)\}', content)
        if biblio_match:
            references.append(f"Bibliography file: {biblio_match.group(1)}")

    section_positions = [(m.start(), m.group(1), 'section') for m in section_pattern.finditer(content)]
    subsection_positions = [(m.start(), m.group(1), 'subsection') for m in subsection_pattern.finditer(content)]
    all_positions = sorted(section_positions + subsection_positions, key=lambda x: x[0])

    text_body = re.sub(r'\\[a-zA-Z]+(\{[^}]*\}|\[[^\]]*\])?', '', content)
    text_body = re.sub(r'\s+', ' ', text_body).strip()

    if all_positions:
        for i, (pos, heading, level) in enumerate(all_positions):
            if i + 1 < len(all_positions):
                next_pos = all_positions[i + 1][0]
                section_text = text_body[pos:next_pos]
            else:
                section_text = text_body[pos:]

            section_text = re.sub(r'\s+', ' ', section_text).strip()
            if level == 'section':
                current_section = "body"
                current_heading = heading
                sections.append({"heading": current_heading, "content": section_text})
            else:
                if sections:
                    sections[-1]["content"] += " " + section_text
    else:
        sections.append({"heading": "", "content": text_body[:5000]})

    return {
        "title": title,
        "authors": authors,
        "abstract": abstract,
        "sections": sections,
        "references": references,
        "tables": tables_data,
        "figures": figures_data
    }
