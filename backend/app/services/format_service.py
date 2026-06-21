import os
from typing import Dict
from app.services.ieee_formatter import generate_ieee_docx


def format_to_docx(structured: Dict, output_path: str, template: str = "ieee") -> str:
    """Formats structured JSON into a DOCX using the requested template.

    Currently supports only 'ieee'. Returns the output_path on success.
    """
    if template != "ieee":
        raise ValueError("Only 'ieee' template is supported currently")

    # The ieee formatter expects a particular parsed_data dict shape; pass through structured
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    return generate_ieee_docx(structured, output_path)
