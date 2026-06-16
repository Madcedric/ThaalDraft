import re
import time
from typing import Any, Dict, List, Optional, Tuple

from app.services.structure.rules import (
    HEADING_TO_LABEL,
    KNOWN_SECTION_PATTERNS,
    CONFIDENCE_WEIGHTS,
    SECTION_ORDER,
)
from app.services.structure.schema import (
    Section,
    DetectedSection,
    StructureConfidenceReport,
)


def _normalize_heading(heading: str) -> str:
    return re.sub(r"[^a-z0-9\s]", "", heading.lower().strip())


def _match_exact_heading(heading: str) -> Optional[Tuple[str, float]]:
    normalized = _normalize_heading(heading)
    if normalized in HEADING_TO_LABEL:
        return HEADING_TO_LABEL[normalized], CONFIDENCE_WEIGHTS["exact_heading_match"]
    return None


def _match_keyword_heading(heading: str) -> Optional[Tuple[str, float]]:
    normalized = _normalize_heading(heading)
    for pattern_label, pattern in KNOWN_SECTION_PATTERNS.items():
        for keyword in pattern.keywords:
            if keyword in normalized or normalized in keyword:
                return pattern.label, CONFIDENCE_WEIGHTS["keyword_match"]
    return None


def _match_position_heuristic(
    heading: str, position_ratio: float
) -> Optional[Tuple[str, float]]:
    normalized = _normalize_heading(heading)
    for pattern_label, pattern in KNOWN_SECTION_PATTERNS.items():
        if pattern.position_weight > 0:
            expected_ratio = 1.0 - pattern.position_weight
            if abs(position_ratio - expected_ratio) < 0.2:
                return pattern.label, CONFIDENCE_WEIGHTS["position_heuristic"]
    return None


def _analyze_content_signals(content: str, heading: str) -> Optional[Tuple[str, float]]:
    if not content:
        return None
    content_lower = content.lower()
    word_count = len(content.split())
    citation_density = len(re.findall(r"\[\d+\]|\(\w+\s+et\s+al\.?,?\s+\d{4}\)", content))
    citation_ratio = citation_density / max(word_count, 1)

    for pattern_label, pattern in KNOWN_SECTION_PATTERNS.items():
        indicator_matches = sum(
            1 for indicator in pattern.content_indicators if indicator in content_lower
        )
        if indicator_matches >= 2:
            return pattern.label, CONFIDENCE_WEIGHTS["content_analysis"]

    if word_count < 500 and citation_ratio > 0.02:
        return "references", CONFIDENCE_WEIGHTS["content_analysis"]

    return None


def _determine_level(heading: str) -> int:
    if re.match(r"^\d+\.\s", heading):
        depth = heading.count(".")
        return min(depth, 3)
    if re.match(r"^#{1,6}\s", heading):
        hashes = len(re.match(r"^(#+)", heading).group(1))
        return min(hashes, 3)
    return 1


def classify_sections(
    parsed: Dict[str, Any],
    format_type: Optional[str] = None,
) -> Tuple[List[Section], StructureConfidenceReport]:
    sections_input = parsed.get("sections", [])
    total_sections = len(sections_input)
    classified_sections: List[Section] = []
    detections: List[DetectedSection] = []
    methods_used = set()
    warnings = []

    title_text = parsed.get("title", "")
    if title_text:
        classified_sections.append(
            Section(
                heading=title_text,
                label="title",
                content="",
                confidence=1.0,
                level=0,
            )
        )
        detections.append(
            DetectedSection(
                heading=title_text,
                label="title",
                confidence=1.0,
                detection_method="format_signal",
            )
        )
        methods_used.add("format_signal")

    abstract_text = parsed.get("abstract", "")
    if abstract_text:
        classified_sections.append(
            Section(
                heading="Abstract",
                label="abstract",
                content=abstract_text,
                confidence=1.0,
                level=1,
            )
        )
        detections.append(
            DetectedSection(
                heading="Abstract",
                label="abstract",
                confidence=1.0,
                detection_method="format_signal",
            )
        )
        methods_used.add("format_signal")

    for idx, sec in enumerate(sections_input):
        heading = sec.get("heading", "") if isinstance(sec, dict) else getattr(sec, "heading", "")
        content = sec.get("content", "") if isinstance(sec, dict) else getattr(sec, "content", "")

        if not heading:
            classified_sections.append(
                Section(
                    heading="Untitled Section",
                    label="other",
                    content=content,
                    confidence=0.3,
                    level=1,
                )
            )
            warnings.append(f"Section at position {idx} has no heading")
            continue

        position_ratio = idx / max(total_sections, 1)
        best_label = "other"
        best_confidence = 0.0
        best_method = "none"

        exact_match = _match_exact_heading(heading)
        if exact_match:
            best_label, best_confidence = exact_match
            best_method = "exact_heading_match"
        else:
            keyword_match = _match_keyword_heading(heading)
            if keyword_match:
                kw_label, kw_conf = keyword_match
                if kw_conf > best_confidence:
                    best_label = kw_label
                    best_confidence = kw_conf
                    best_method = "keyword_match"

            position_match = _match_position_heuristic(heading, position_ratio)
            if position_match:
                pos_label, pos_conf = position_match
                if pos_conf > best_confidence:
                    best_label = pos_label
                    best_confidence = pos_conf
                    best_method = "position_heuristic"

            content_match = _analyze_content_signals(content, heading)
            if content_match:
                con_label, con_conf = content_match
                if con_conf > best_confidence:
                    best_label = con_label
                    best_confidence = con_conf
                    best_method = "content_analysis"

        if format_type == "docx":
            best_confidence = min(best_confidence + 0.05, 1.0)
            methods_used.add("format_signal")
        elif format_type in ("latex", "md"):
            if best_method == "exact_heading_match":
                best_confidence = min(best_confidence + 0.05, 1.0)

        methods_used.add(best_method)
        level = _determine_level(heading)

        classified_sections.append(
            Section(
                heading=heading,
                label=best_label,
                content=content,
                confidence=round(best_confidence, 3),
                level=level,
            )
        )
        detections.append(
            DetectedSection(
                heading=heading,
                label=best_label,
                confidence=round(best_confidence, 3),
                detection_method=best_method,
            )
        )

    references = parsed.get("references", [])
    if references and not any(s.label == "references" for s in classified_sections):
        ref_content = "\n".join(references) if isinstance(references[0], str) else str(references)
        classified_sections.append(
            Section(
                heading="References",
                label="references",
                content=ref_content,
                confidence=0.9,
                level=1,
            )
        )
        detections.append(
            DetectedSection(
                heading="References",
                label="references",
                confidence=0.9,
                detection_method="format_signal",
            )
        )
        methods_used.add("format_signal")

    detected_labels = list({s.label for s in classified_sections})
    expected_labels = ["abstract", "introduction", "methods", "results", "discussion", "conclusion", "references"]
    missing = [l for l in expected_labels if l not in detected_labels]

    confidences = [d.confidence for d in detections]
    overall = sum(confidences) / len(confidences) if confidences else 0.0

    report = StructureConfidenceReport(
        overall_confidence=round(overall, 3),
        section_detections=detections,
        detected_labels=detected_labels,
        missing_labels=missing,
        detection_methods_used=sorted(methods_used),
        warnings=warnings,
    )

    return classified_sections, report
