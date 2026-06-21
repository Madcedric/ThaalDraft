"""
LaTeX Exporter — Phase 5
Generates properly structured LaTeX source for major journal templates.
Supports: IEEE, Elsevier, Springer, Nature, APA, ACM.
"""
from typing import Any, Dict, List


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    replacements = [
        ('\\', r'\textbackslash{}'),
        ('&', r'\&'),
        ('%', r'\%'),
        ('$', r'\$'),
        ('#', r'\#'),
        ('^', r'\^{}'),
        ('{', r'\{'),
        ('}', r'\}'),
        ('~', r'\~{}'),
        ('_', r'\_'),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    return text


def _get_author_names(structured_data: Dict) -> List[str]:
    authors = structured_data.get("authors", [])
    if isinstance(authors, list) and authors:
        if isinstance(authors[0], dict):
            return [a.get("name", str(a)) for a in authors if a.get("name")]
        return [str(a) for a in authors]
    return []


def _build_references_latex(references: List, numbering: bool = True) -> str:
    if not references:
        return ""
    lines = ["\\begin{thebibliography}{99}"]
    for idx, ref in enumerate(references):
        raw = ref.get("raw_text", str(ref)) if isinstance(ref, dict) else str(ref)
        doi = ref.get("doi", "") if isinstance(ref, dict) else ""
        bibitem = f"\\bibitem{{ref{idx+1}}}\n{_escape_latex(raw)}"
        if doi:
            bibitem += f"\n\\url{{https://doi.org/{doi}}}"
        lines.append(bibitem)
    lines.append("\\end{thebibliography}")
    return "\n".join(lines)


def generate_ieee_latex(structured_data: Dict) -> str:
    title = _escape_latex(structured_data.get("title", "Untitled"))
    abstract = _escape_latex(structured_data.get("abstract", ""))
    authors = _get_author_names(structured_data)
    keywords = structured_data.get("keywords", [])
    sections = structured_data.get("sections", [])
    references = structured_data.get("references", [])

    author_str = " \\and ".join(_escape_latex(a) for a in authors) if authors else "Author Name"
    kw_str = ", ".join(_escape_latex(k) for k in keywords) if keywords else ""

    body_parts = []
    roman = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X"]
    for idx, sec in enumerate(sections):
        heading = _escape_latex(sec.get("heading", "") if isinstance(sec, dict) else "")
        content = _escape_latex(sec.get("content", "") if isinstance(sec, dict) else "")
        if heading:
            body_parts.append(f"\\section{{{heading}}}")
        if content:
            body_parts.append(content)
    body = "\n\n".join(body_parts)

    refs = _build_references_latex(references, numbering=True)

    return f"""\\documentclass[conference]{{IEEEtran}}
\\usepackage{{url}}
\\usepackage{{hyperref}}
\\usepackage{{amsmath}}

\\title{{{title}}}
\\author{{{author_str}}}

\\begin{{document}}

\\maketitle

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

\\begin{{IEEEkeywords}}
{kw_str}
\\end{{IEEEkeywords}}

{body}

{refs}

\\end{{document}}
"""


def generate_elsevier_latex(structured_data: Dict) -> str:
    title = _escape_latex(structured_data.get("title", "Untitled"))
    abstract = _escape_latex(structured_data.get("abstract", ""))
    authors = _get_author_names(structured_data)
    keywords = structured_data.get("keywords", [])
    sections = structured_data.get("sections", [])
    references = structured_data.get("references", [])

    author_entries = "\n".join(f"\\author{{{_escape_latex(a)}}}" for a in authors) if authors else "\\author{Author Name}"
    kw_str = ", ".join(_escape_latex(k) for k in keywords)

    body_parts = []
    for sec in sections:
        heading = _escape_latex(sec.get("heading", "") if isinstance(sec, dict) else "")
        content = _escape_latex(sec.get("content", "") if isinstance(sec, dict) else "")
        level = sec.get("level", 1) if isinstance(sec, dict) else 1
        cmd = "\\section" if level == 1 else "\\subsection" if level == 2 else "\\subsubsection"
        if heading:
            body_parts.append(f"{cmd}{{{heading}}}")
        if content:
            body_parts.append(content)
    body = "\n\n".join(body_parts)

    refs = _build_references_latex(references)

    return f"""\\documentclass[preprint,12pt]{{elsarticle}}
\\usepackage{{url}}
\\usepackage{{hyperref}}
\\usepackage{{amsmath}}

\\journal{{Elsevier Journal}}

\\begin{{document}}

\\begin{{frontmatter}}

\\title{{{title}}}
{author_entries}

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

\\begin{{keyword}}
{kw_str}
\\end{{keyword}}

\\end{{frontmatter}}

{body}

{refs}

\\end{{document}}
"""


def generate_springer_latex(structured_data: Dict) -> str:
    title = _escape_latex(structured_data.get("title", "Untitled"))
    abstract = _escape_latex(structured_data.get("abstract", ""))
    authors = _get_author_names(structured_data)
    sections = structured_data.get("sections", [])
    references = structured_data.get("references", [])
    keywords = structured_data.get("keywords", [])

    author_str = " \\and ".join(_escape_latex(a) for a in authors) if authors else "Author Name"
    kw_str = ", ".join(_escape_latex(k) for k in keywords)

    body_parts = []
    for sec in sections:
        heading = _escape_latex(sec.get("heading", "") if isinstance(sec, dict) else "")
        content = _escape_latex(sec.get("content", "") if isinstance(sec, dict) else "")
        level = sec.get("level", 1) if isinstance(sec, dict) else 1
        cmd = "\\section" if level == 1 else "\\subsection"
        if heading:
            body_parts.append(f"{cmd}{{{heading}}}")
        if content:
            body_parts.append(content)
    body = "\n\n".join(body_parts)
    refs = _build_references_latex(references)

    return f"""\\documentclass{{llncs}}
\\usepackage{{url}}
\\usepackage{{hyperref}}

\\title{{{title}}}
\\author{{{author_str}}}

\\begin{{document}}
\\maketitle

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

\\keywords{{{kw_str}}}

{body}

{refs}

\\end{{document}}
"""


def generate_nature_latex(structured_data: Dict) -> str:
    title = _escape_latex(structured_data.get("title", "Untitled"))
    abstract = _escape_latex(structured_data.get("abstract", ""))
    authors = _get_author_names(structured_data)
    sections = structured_data.get("sections", [])
    references = structured_data.get("references", [])

    author_str = ", ".join(_escape_latex(a) for a in authors) if authors else "Author Name"

    body_parts = []
    for sec in sections:
        heading = _escape_latex(sec.get("heading", "") if isinstance(sec, dict) else "")
        content = _escape_latex(sec.get("content", "") if isinstance(sec, dict) else "")
        if heading:
            body_parts.append(f"\\section{{{heading}}}")
        if content:
            body_parts.append(content)
    body = "\n\n".join(body_parts)
    refs = _build_references_latex(references, numbering=True)

    return f"""\\documentclass[12pt]{{article}}
\\usepackage[margin=1in]{{geometry}}
\\usepackage{{url}}
\\usepackage{{hyperref}}
\\usepackage{{setspace}}
\\doublespacing

\\title{{{title}}}
\\author{{{author_str}}}
\\date{{}}

\\begin{{document}}
\\maketitle

\\begin{{abstract}}
{abstract}
\\end{{abstract}}

{body}

{refs}

\\end{{document}}
"""


LATEX_GENERATORS = {
    "ieee": generate_ieee_latex,
    "elsevier": generate_elsevier_latex,
    "springer": generate_springer_latex,
    "nature": generate_nature_latex,
    # Fallback: use IEEE template structure for acm, apa, mla
    "acm": generate_ieee_latex,
    "apa": generate_nature_latex,
    "mla": generate_nature_latex,
}


def export_latex(structured_data: Dict, template_id: str) -> str:
    """Return a complete LaTeX source string for the given template."""
    generator = LATEX_GENERATORS.get(template_id, generate_ieee_latex)
    return generator(structured_data)
