"""Export Engine — V2.

Generates DOCX, PDF, LaTeX, and ZIP package exports from StructuredManuscript.
"""
import io
import logging
import os
import shutil
import tempfile
import time
import zipfile
from typing import Any, Dict, List, Optional

from app.services.manuscript.model import StructuredManuscript
from app.services.formatting.engine_v2 import format_manuscript, TEMPLATE_CONFIGS

logger = logging.getLogger(__name__)


# ─── LaTeX Export ──────────────────────────────────────────────────────────────

LATEX_TEMPLATE = r"""\documentclass[{cols}]{{article}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{geometry}}
\geometry{{{margins}}}
\usepackage{{setspace}}
\usepackage{{amsmath,amssymb}}
\usepackage{{graphicx}}
\usepackage{{booktabs}}
\usepackage{{hyperref}}
\usepackage{{{bib_style}}}
\usepackage{{caption}}
\usepackage{{fancyhdr}}
\pagestyle{{fancy}}
\fancyhf{{}}
\fancyhead[C]{{\small\leftmark}}
\fancyfoot[C]{{\thepage}}
\renewcommand{{\headrulewidth}}{{0.4pt}}

\title{{\textbf{{{title}}}}}
\author{{{authors}}}
\date{{}}

\begin{{document}}
\maketitle
{abstract_section}
{keywords_section}
{body}
{references_section}
\end{{document}}
"""


def export_latex(
    manuscript: StructuredManuscript,
    template_id: str = "ieee",
    output_dir: str = "exports",
    filename: Optional[str] = None,
) -> str:
    """Export manuscript as LaTeX (.tex). Returns file path."""
    start = time.time()

    config = TEMPLATE_CONFIGS.get(template_id, TEMPLATE_CONFIGS["ieee"])

    # Build LaTeX source
    cols = "twocolumn" if config.two_column else "onecolumn"
    margins_str = ", ".join(f"{k}={v}in" for k, v in config.margins.items())
    bib_style = _get_bib_style(template_id)

    # Title
    title = manuscript.title or "Untitled"

    # Authors
    authors = ""
    if manuscript.authors:
        author_parts = []
        for a in manuscript.authors:
            if a.affiliation:
                author_parts.append(f"{a.name}^{{*}}")
            else:
                author_parts.append(a.name)
        authors = " and ".join(author_parts)

    # Abstract
    abstract_section = ""
    if manuscript.abstract:
        abstract_section = (
            f"\\begin{{abstract}}\n{manuscript.abstract}\n\\end{{abstract}}"
        )

    # Keywords
    keywords_section = ""
    if manuscript.keywords:
        kw = ", ".join(manuscript.keywords)
        keywords_section = f"\\noindent\\textbf{{Keywords:}} {kw}\n\n"

    # Body
    body_parts = []
    for sec in manuscript.sections:
        if sec.label.value in ("title", "abstract", "keywords"):
            continue
        if sec.heading:
            cmd = _get_section_cmd(sec.level, template_id)
            body_parts.append(f"{cmd}{{{sec.heading}}}")
        if sec.content:
            # Escape special LaTeX characters
            content = _escape_latex(sec.content)
            body_parts.append(content)
    body = "\n\n".join(body_parts)

    # References
    references_section = ""
    if manuscript.references:
        ref_entries = []
        for ref in manuscript.references:
            ref_entries.append(f"\\bibitem{{{ref.index}}} {_format_ref_latex(ref)}")
        references_section = (
            f"\\begin{{thebibliography}}{{99}}\n"
            + "\n".join(ref_entries)
            + "\n\\end{{thebibliography}}"
        )

    latex_source = LATEX_TEMPLATE.format(
        cols=cols,
        margins=margins_str,
        bib_style=bib_style,
        title=title,
        authors=authors,
        abstract_section=abstract_section,
        keywords_section=keywords_section,
        body=body,
        references_section=references_section,
    )

    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename or f"{template_id}_manuscript.tex")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(latex_source)

    elapsed = (time.time() - start) * 1000
    logger.info(f"LaTeX export completed in {elapsed:.0f}ms -> {output_path}")
    return output_path


def _escape_latex(text: str) -> str:
    """Escape special LaTeX characters."""
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    for char, replacement in replacements.items():
        text = text.replace(char, replacement)
    return text


def _format_ref_latex(ref) -> str:
    """Format a reference for LaTeX bibliography."""
    parts = []
    if ref.authors:
        parts.append(", ".join(ref.authors))
    if ref.title:
        parts.append(f"{{{ref.title}}}")
    if ref.journal:
        parts.append(f"\\textit{{{ref.journal}}}")
    if ref.volume:
        parts.append(f"\\textbf{{{ref.volume}}}")
    if ref.pages:
        parts.append(f"pp.~{ref.pages}")
    if ref.year:
        parts.append(f"({ref.year})")
    if ref.doi:
        parts.append(f"\\url{{https://doi.org/{ref.doi}}}")
    return ", ".join(parts) if parts else ref.raw_text


def _get_bib_style(template_id: str) -> str:
    """Get BibTeX style for template."""
    styles = {
        "ieee": "IEEEtran",
        "acm": "ACM-Reference-Format",
        "springer": "splncs03",
        "apa": "apalike",
        "mla": "plainnat",
        "nature": "naturemag",
        "elsevier": "elsarticle-num",
    }
    return styles.get(template_id, "plain")


def _get_section_cmd(level: int, template_id: str) -> str:
    """Get LaTeX section command for level."""
    cmds = {1: r"\section", 2: r"\subsection", 3: r"\subsubsection"}
    return cmds.get(level, r"\section")


# ─── ZIP Package Export ────────────────────────────────────────────────────────

def export_zip_package(
    manuscript: StructuredManuscript,
    template_id: str = "ieee",
    output_dir: str = "exports",
    include_sources: bool = True,
    include_figures: bool = True,
    filename: Optional[str] = None,
) -> str:
    """Export manuscript as a complete ZIP package with all sources.

    Package includes:
    - LaTeX source (.tex)
    - DOCX formatted document
    - Figures (if any)
    - metadata.json
    """
    start = time.time()
    os.makedirs(output_dir, exist_ok=True)

    zip_name = filename or f"{template_id}_package.zip"
    zip_path = os.path.join(output_dir, zip_name)

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        # 1. DOCX
        docx_path = format_manuscript(manuscript, template_id, output_dir)
        zf.write(docx_path, f"manuscript/{os.path.basename(docx_path)}")

        # 2. LaTeX source
        if include_sources:
            tex_path = export_latex(manuscript, template_id, output_dir, f"{template_id}_manuscript.tex")
            zf.write(tex_path, f"manuscript/{os.path.basename(tex_path)}")

        # 3. Figures
        if include_figures:
            for sec in manuscript.sections:
                for fig in sec.figures:
                    if fig.image_path and os.path.exists(fig.image_path):
                        arcname = f"figures/{os.path.basename(fig.image_path)}"
                        zf.write(fig.image_path, arcname)

        # 4. Metadata
        import json
        metadata = {
            "template": template_id,
            "title": manuscript.title,
            "authors": [a.name for a in manuscript.authors],
            "word_count": manuscript.word_count,
            "section_count": manuscript.section_count,
            "reference_count": manuscript.reference_count,
            "exports": ["docx", "tex"] if include_sources else ["docx"],
        }
        zf.writestr("metadata.json", json.dumps(metadata, indent=2))

    elapsed = (time.time() - start) * 1000
    logger.info(f"ZIP package export completed in {elapsed:.0f}ms -> {zip_path}")
    return zip_path


# ─── Unified Export ────────────────────────────────────────────────────────────

def export_manuscript(
    manuscript: StructuredManuscript,
    format_type: str,
    template_id: str = "ieee",
    output_dir: str = "exports",
    filename: Optional[str] = None,
    **kwargs,
) -> Optional[str]:
    """Unified export entry point.

    Args:
        manuscript: StructuredManuscript to export.
        format_type: 'docx', 'pdf', 'latex', or 'zip'.
        template_id: Journal template to use.
        output_dir: Output directory.
        filename: Custom filename (optional).
        **kwargs: Additional format-specific options.

    Returns:
        File path or None on failure.
    """
    if format_type == "docx":
        return export_docx(manuscript, template_id, output_dir, filename)
    elif format_type == "pdf":
        return export_pdf(manuscript, template_id, output_dir, filename)
    elif format_type == "latex":
        return export_latex(manuscript, template_id, output_dir, filename)
    elif format_type == "zip":
        return export_zip_package(manuscript, template_id, output_dir, **kwargs)
    else:
        logger.error(f"Unsupported export format: {format_type}")
        return None


# ─── Re-export existing functions ──────────────────────────────────────────────

def export_docx(
    manuscript: StructuredManuscript,
    template_id: str = "ieee",
    output_dir: str = "exports",
    filename: Optional[str] = None,
) -> str:
    """Export manuscript as DOCX. Returns file path."""
    return format_manuscript(manuscript, template_id, output_dir)


def export_pdf(
    manuscript: StructuredManuscript,
    template_id: str = "ieee",
    output_dir: str = "exports",
    filename: Optional[str] = None,
) -> Optional[str]:
    """Export manuscript as PDF. Returns file path or None."""
    docx_path = export_docx(manuscript, template_id, output_dir)
    pdf_path = os.path.join(output_dir, filename or f"{template_id}_manuscript.pdf")
    try:
        from app.services.pdf_service import convert_docx_to_pdf
        if convert_docx_to_pdf(docx_path, pdf_path):
            return pdf_path
    except Exception as e:
        logger.warning(f"PDF conversion failed: {e}")
    return None


def get_supported_templates() -> List[str]:
    """Return list of supported template IDs."""
    return list(TEMPLATE_CONFIGS.keys())


def get_supported_formats() -> List[str]:
    """Return list of supported export formats."""
    return ["docx", "pdf", "latex", "zip"]
