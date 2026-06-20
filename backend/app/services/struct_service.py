import re
import time
import logging
from typing import Any, Dict, List, Optional, Tuple

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

logger = logging.getLogger(__name__)

_spacy_nlp = None
_sentence_model = None


def _get_spacy_nlp():
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            import spacy
            _spacy_nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(f"spaCy model not available: {e}")
            _spacy_nlp = False
    return _spacy_nlp if _spacy_nlp is not False else None


def _get_sentence_model():
    global _sentence_model
    if _sentence_model is None:
        try:
            from sentence_transformers import SentenceTransformer
            _sentence_model = SentenceTransformer("all-MiniLM-L6-v2")
        except Exception as e:
            logger.warning(f"SentenceTransformer not available: {e}")
            _sentence_model = False
    return _sentence_model if _sentence_model is not False else None


def _spacy_extract_entities(text: str) -> Dict[str, List[str]]:
    nlp = _get_spacy_nlp()
    if not nlp:
        return {}
    try:
        doc = nlp(text[:10000])
        entities = {}
        for ent in doc.ents:
            label = ent.label_
            if label not in entities:
                entities[label] = []
            entities[label].append(ent.text)
        return entities
    except Exception:
        return {}


def _spacy_classify_section_heading(heading: str, content: str) -> Optional[Tuple[str, float]]:
    nlp = _get_spacy_nlp()
    if not nlp:
        return None
    try:
        combined = f"{heading}. {content[:500]}"
        doc = nlp(combined)
        heading_lower = heading.lower().strip()

        if any(ent.label_ in ("DATE", "CARDINAL") for ent in doc.ents):
            if any(kw in heading_lower for kw in ["introduction", "background", "overview"]):
                return "introduction", 0.9

        org_count = sum(1 for ent in doc.ents if ent.label_ == "ORG")
        method_keywords = ["method", "approach", "algorithm", "procedure", "technique", "model", "architecture"]
        if any(kw in heading_lower for kw in method_keywords) or org_count > 2:
            return "methods", 0.85

        return None
    except Exception:
        return None


def _semantic_classify_heading(heading: str) -> Optional[Tuple[str, float]]:
    model = _get_sentence_model()
    if not model:
        return None
    try:
        section_prototypes = {
            "introduction": "introduction background motivation overview of the research problem and objectives",
            "methods": "methodology approach experimental design algorithm implementation procedure technique",
            "results": "results findings evaluation performance metrics experimental outcomes data analysis",
            "discussion": "discussion interpretation implications comparison analysis of results and limitations",
            "conclusion": "conclusion summary final remarks future work contributions and findings",
            "related_work": "related work literature review prior research background survey of existing approaches",
            "abstract": "abstract summary overview of the paper",
            "references": "references bibliography citations list of cited works",
        }

        heading_embedding = model.encode([heading])
        section_names = list(section_prototypes.keys())
        section_texts = list(section_prototypes.values())
        section_embeddings = model.encode(section_texts)

        from sentence_transformers import util
        similarities = util.cos_sim(heading_embedding, section_embeddings)[0]
        best_idx = similarities.argmax().item()
        best_score = similarities[best_idx].item()

        if best_score > 0.5:
            return section_names[best_idx], min(best_score + 0.1, 1.0)
        return None
    except Exception:
        return None


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

    for i, section in enumerate(classified_sections):
        if section.label == "other" and section.confidence < 0.5:
            spacy_result = _spacy_classify_section_heading(section.heading, section.content)
            if spacy_result:
                new_label, new_conf = spacy_result
                if new_conf > section.confidence:
                    classified_sections[i] = Section(
                        heading=section.heading,
                        label=new_label,
                        content=section.content,
                        confidence=round(new_conf, 3),
                        level=section.level,
                    )
                    logger.info(f"spaCy reclassified '{section.heading}' -> {new_label} ({new_conf:.2f})")

            if classified_sections[i].label == "other":
                semantic_result = _semantic_classify_heading(section.heading)
                if semantic_result:
                    new_label, new_conf = semantic_result
                    if new_conf > classified_sections[i].confidence:
                        classified_sections[i] = Section(
                            heading=section.heading,
                            label=new_label,
                            content=section.content,
                            confidence=round(new_conf, 3),
                            level=section.level,
                        )
                        logger.info(f"Semantic reclassified '{section.heading}' -> {new_label} ({new_conf:.2f})")

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
                authors.append(Author(
                    name=item.get("name", ""),
                    affiliation=item.get("affiliation"),
                    email=item.get("email"),
                ))

    spacy_entities = _spacy_extract_entities(
        " ".join(s.content[:500] for s in classified_sections[:5])
    )

    tables = parsed.get("tables", [])
    figures = parsed.get("figures", [])

    processing_time = (time.time() - start_time) * 1000

    methods_used = set()
    if spacy_entities:
        methods_used.add("spacy_ner")
    if _get_sentence_model():
        methods_used.add("sentence_transformers")
    methods_used.add("deterministic")

    processing_meta = ProcessingMetadata(
        file_type=file_type,
        parser_used=f"{file_type}_parser",
        classification_method="+".join(sorted(methods_used)),
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
