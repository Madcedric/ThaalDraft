import re
from typing import Optional


def parse_pdf(file_path: str) -> dict:
    """Parses a PDF file and extracts structured text using PyMuPDF."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF is required for PDF parsing. Install with: pip install PyMuPDF")

    doc = fitz.open(file_path)

    title = ""
    authors = []
    abstract = ""
    sections = []
    references = []
    figures_data = []
    tables_data = []

    current_section = "general"
    current_heading = ""
    full_text = ""

    abstract_pattern = re.compile(r'^(abstract|summary)$', re.IGNORECASE)
    reference_pattern = re.compile(r'^(references|bibliography|works cited)$', re.IGNORECASE)
    heading_pattern = re.compile(r'^(\d+\.?\s+|[A-Z][A-Z\s]{2,})$')
    figure_pattern = re.compile(r'^(fig\.|figure)\s*\d+[:\.\-]', re.IGNORECASE)
    author_pattern = re.compile(r'^(?:by\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s*,\s*[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)*)', re.IGNORECASE)

    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text()
        full_text += text + "\n"

        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            if not title and len(line) < 150 and not line.startswith(("1.", "2.", "3.", "I.", "II.", "III")):
                title = line
                continue

            if not authors and author_pattern.match(line) and len(line) < 200:
                author_text = line.replace("by ", "", 1) if line.lower().startswith("by ") else line
                authors = [a.strip() for a in author_text.split(",")]
                continue

            if abstract_pattern.match(line):
                current_section = "abstract"
                continue

            if reference_pattern.match(line):
                current_section = "references"
                continue

            if heading_pattern.match(line) and len(line) < 100:
                current_section = "body"
                current_heading = line
                sections.append({"heading": current_heading, "content": ""})
                continue

            if figure_pattern.match(line):
                figures_data.append(line)
                continue

            if current_section == "abstract":
                abstract += line + "\n"
            elif current_section == "references":
                references.append(line)
            elif current_section == "body":
                if sections:
                    sections[-1]["content"] += line + "\n"
                else:
                    sections.append({"heading": "", "content": line + "\n"})
                    current_section = "body"
            else:
                if sections:
                    sections[-1]["content"] += line + "\n"
                else:
                    sections.append({"heading": "", "content": line + "\n"})
                    current_section = "body"

    doc.close()

    return {
        "title": title,
        "authors": authors,
        "abstract": abstract.strip(),
        "sections": sections,
        "references": references,
        "tables": tables_data,
        "figures": figures_data
    }
