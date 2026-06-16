import re
import time
from typing import Any, Dict, List

from app.services.structure.classifier import classify_sections
from app.services.structure.metadata_extractor import (
    extract_metadata as extract_doc_metadata,
    extract_references,
)
from app.services.structure.validator import validate_structure, generate_confidence_report
from app.services.structure.schema import (
    StructuredDocument,
    Section,
    Reference,
    ProcessingMetadata,
    DocumentMetadata,
    StructureConfidenceReport,
    Author,
)


def extract_citations_from_text(text: str) -> List[str]:
    if not text:
        return []
    citations = set()
    for m in re.findall(r"\[\s*\d+(?:[\-\,\s\d]*)\s*\]", text):
        citations.add(m)
    for m in re.findall(r"[A-Z][A-Za-z]+(?: et al\.)?,? \d{4}", text):
        citations.add(m)
    return list(citations)


def normalize_classification(
    parsed: Dict[str, Any],
    classification: Dict[str, Any] = None,
    file_type: str = "unknown",
) -> Dict[str, Any]:
    start_time = time.time()

    classified_sections, confidence_report = classify_sections(parsed, format_type=file_type)

    doc_metadata = extract_doc_metadata(parsed)
    references = extract_references(parsed)

    all_citations = []
    for section in classified_sections:
        all_citations.extend(extract_citations_from_text(section.content))
    unique_citations = list(dict.fromkeys(all_citations))

    title_text = parsed.get("title", "")
    raw_authors = parsed.get("authors", [])
    authors = []
    if isinstance(raw_authors, list):
        for item in raw_authors:
            if isinstance(item, str):
                authors.append(Author(name=item))
            elif isinstance(item, dict):
                authors.append(
                    Author(
                        name=item.get("name", ""),
                        affiliation=item.get("affiliation"),
                        email=item.get("email"),
                    )
                )

    tables = parsed.get("tables", [])
    figures = parsed.get("figures", [])

    processing_time = (time.time() - start_time) * 1000

    processing_meta = ProcessingMetadata(
        file_type=file_type,
        parser_used=f"{file_type}_parser",
        classification_method="deterministic",
        processing_time_ms=round(processing_time, 2),
    )

    structured = StructuredDocument(
        title=title_text,
        authors=authors,
        abstract=parsed.get("abstract", ""),
        keywords=doc_metadata.keywords,
        sections=classified_sections,
        references=references,
        citations=unique_citations,
        tables=tables,
        figures=figures,
        metadata=doc_metadata,
        processing_metadata=processing_meta,
        confidence_report=confidence_report,
    )

    validation = validate_structure(structured)
    if validation.warnings:
        confidence_report.warnings.extend(validation.warnings)

    result = structured.model_dump()

    result["_backward_compatible"] = {
        "title": structured.title,
        "authors": [a.name for a in structured.authors],
        "abstract": structured.abstract,
        "sections": [
            {"heading": s.heading, "label": s.label, "content": s.content}
            for s in structured.sections
        ],
        "references": [r.raw_text for r in structured.references],
        "tables": structured.tables,
        "figures": structured.figures,
        "citations": structured.citations,
    }

    return result


def get_backward_compatible(structured_json: Dict[str, Any]) -> Dict[str, Any]:
    if "_backward_compatible" in structured_json:
        return structured_json["_backward_compatible"]

    return {
        "title": structured_json.get("title"),
        "authors": [
            a.get("name", "") if isinstance(a, dict) else str(a)
            for a in structured_json.get("authors", [])
        ],
        "abstract": structured_json.get("abstract", ""),
        "sections": structured_json.get("sections", []),
        "references": [
            r.get("raw_text", str(r)) if isinstance(r, dict) else str(r)
            for r in structured_json.get("references", [])
        ],
        "tables": structured_json.get("tables", []),
        "figures": structured_json.get("figures", []),
        "citations": structured_json.get("citations", []),
    }
