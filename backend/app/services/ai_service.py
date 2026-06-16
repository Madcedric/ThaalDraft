import os
import json
from typing import Any, Dict

from app.services.structure.classifier import classify_sections


def classify_structure(parsed: Dict[str, Any]) -> Dict[str, Any]:
    classified_sections, confidence_report = classify_sections(parsed)

    classification = {
        "sections": [
            {"heading": s.heading, "label": s.label, "confidence": s.confidence}
            for s in classified_sections
        ],
        "confidence_report": {
            "overall_confidence": confidence_report.overall_confidence,
            "detected_labels": confidence_report.detected_labels,
            "missing_labels": confidence_report.missing_labels,
            "detection_methods_used": confidence_report.detection_methods_used,
            "warnings": confidence_report.warnings,
        },
    }

    return {
        "raw": json.dumps(classification),
        "classification": classification,
        "method": "deterministic",
    }
