from typing import Any, Dict, List

from app.services.structure.schema import (
    StructuredDocument,
    StructureConfidenceReport,
    StructureValidationResult,
)


REQUIRED_SECTIONS = ["abstract", "introduction", "methods", "results", "discussion", "conclusion", "references"]

RECOMMENDED_SECTIONS = ["abstract", "introduction", "methods", "results", "discussion", "conclusion"]

LOW_CONFIDENCE_THRESHOLD = 0.5
MEDIUM_CONFIDENCE_THRESHOLD = 0.7


def validate_structure(structured: StructuredDocument) -> StructureValidationResult:
    errors = []
    warnings = []
    completeness_score = 0.0

    if not structured.title:
        warnings.append("No title detected")

    if not structured.authors:
        warnings.append("No authors detected")

    if not structured.abstract or len(structured.abstract.strip()) < 10:
        warnings.append("Abstract is missing or too short")

    if not structured.sections:
        errors.append("No sections detected")
        return StructureValidationResult(
            is_valid=False,
            errors=errors,
            warnings=warnings,
            completeness_score=0.0,
        )

    detected_labels = {s.label for s in structured.sections}
    missing_required = [label for label in REQUIRED_SECTIONS if label not in detected_labels]
    if missing_required:
        warnings.append(f"Missing recommended sections: {', '.join(missing_required)}")

    if not structured.references:
        warnings.append("No references detected")

    low_confidence = [
        s for s in structured.sections if s.confidence < LOW_CONFIDENCE_THRESHOLD
    ]
    if low_confidence:
        headings = [s.heading for s in low_confidence]
        warnings.append(f"Low confidence detections: {', '.join(headings[:3])}")

    label_counts = {}
    for s in structured.sections:
        label_counts[s.label] = label_counts.get(s.label, 0) + 1
    duplicates = {label: count for label, count in label_counts.items() if count > 1}
    if duplicates:
        warnings.append(f"Duplicate section labels detected: {duplicates}")

    section_score = len(detected_labels & set(RECOMMENDED_SECTIONS)) / len(RECOMMENDED_SECTIONS)
    confidence_values = [s.confidence for s in structured.sections]
    avg_confidence = sum(confidence_values) / len(confidence_values) if confidence_values else 0
    title_bonus = 0.05 if structured.title else 0
    abstract_bonus = 0.05 if structured.abstract else 0
    refs_bonus = 0.05 if structured.references else 0

    completeness_score = min(
        (section_score * 0.6 + avg_confidence * 0.3 + title_bonus + abstract_bonus + refs_bonus),
        1.0,
    )

    is_valid = len(errors) == 0 and completeness_score >= 0.3

    return StructureValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        completeness_score=round(completeness_score, 3),
    )


def generate_confidence_report(
    structured: StructuredDocument,
) -> StructureConfidenceReport:
    report = structured.confidence_report

    if not report.section_detections:
        detections = []
        for section in structured.sections:
            from app.services.structure.schema import DetectedSection

            detections.append(
                DetectedSection(
                    heading=section.heading,
                    label=section.label,
                    confidence=section.confidence,
                    detection_method="unknown",
                )
            )
        report.section_detections = detections

    if not report.detected_labels:
        report.detected_labels = list({s.label for s in structured.sections})

    if not report.missing_labels:
        detected = set(report.detected_labels)
        report.missing_labels = [
            label for label in REQUIRED_SECTIONS if label not in detected
        ]

    if not report.detection_methods_used:
        methods = set()
        for detection in report.section_detections:
            methods.add(detection.detection_method)
        report.detection_methods_used = sorted(methods)

    confidences = [d.confidence for d in report.section_detections]
    report.overall_confidence = (
        round(sum(confidences) / len(confidences), 3) if confidences else 0.0
    )

    if report.overall_confidence < MEDIUM_CONFIDENCE_THRESHOLD:
        report.warnings.append(
            f"Overall confidence is below threshold ({report.overall_confidence:.1%})"
        )

    if report.missing_labels:
        report.warnings.append(
            f"Missing sections: {', '.join(report.missing_labels)}"
        )

    return report
