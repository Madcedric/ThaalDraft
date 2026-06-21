"""Custom Journal Builder — V2 Formatting Studio.

Allows users to create custom journal templates by specifying:
- Font settings (body, title, headings)
- Margins
- Column layout
- Citation style
- Heading hierarchy
- Keywords/abstract requirements

Custom templates are stored in Supabase and extend the built-in templates.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests

from app.services.formatting.schema import (
    FormatTemplate,
    FontConfig,
    MarginConfig,
    HeadingConfig,
    CitationStyleConfig,
)

logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def _headers() -> Dict[str, str]:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


def create_custom_template(
    user_id: str,
    template_config: Dict[str, Any],
    template_name: Optional[str] = None,
    base_template_id: Optional[str] = None,
) -> Optional[FormatTemplate]:
    """Create a custom journal template.

    Args:
        user_id: The user creating the template.
        template_config: Template configuration dict with keys matching FormatTemplate.
        template_name: Human-readable name for the template.
        base_template_id: Optional base template to extend.

    Returns:
        FormatTemplate if created, None on error.
    """
    # If base template provided, merge configs
    if base_template_id:
        from app.services.formatting.templates import get_template
        base = get_template(base_template_id)
        if base:
            base_dict = base.model_dump()
            base_dict.update(template_config)
            template_config = base_dict

    template_id = f"custom_{user_id}_{template_config.get('name', 'unnamed').lower().replace(' ', '_')}"

    # Build FormatTemplate
    try:
        ft = FormatTemplate(
            id=template_id,
            name=template_name or template_config.get("name", "Custom Template"),
            description=template_config.get("description", "User-created custom template"),
            body_font=FontConfig(**template_config.get("body_font", {})),
            title_font=FontConfig(**template_config.get("title_font", {})),
            abstract_font=FontConfig(**template_config.get("abstract_font", {})),
            margins=MarginConfig(**template_config.get("margins", {})),
            headings=[HeadingConfig(**h) for h in template_config.get("headings", [])],
            citation_style=CitationStyleConfig(**template_config.get("citation_style", {})),
            column_count=template_config.get("column_count", 1),
            line_spacing=template_config.get("line_spacing", 1.0),
            abstract_label=template_config.get("abstract_label", "Abstract"),
            references_label=template_config.get("references_label", "References"),
            figure_caption_prefix=template_config.get("figure_caption_prefix", "Fig."),
            table_caption_prefix=template_config.get("table_caption_prefix", "TABLE"),
            requires_keywords=template_config.get("requires_keywords", False),
            keywords_label=template_config.get("keywords_label", "Keywords"),
            two_column=template_config.get("two_column", False),
        )
    except Exception as e:
        logger.error(f"Failed to create FormatTemplate: {e}")
        return None

    # Save to Supabase
    if SUPABASE_URL and SUPABASE_KEY:
        try:
            row = {
                "user_id": user_id,
                "template_id": template_id,
                "template_name": ft.name,
                "template_config": ft.model_dump(),
                "base_template_id": base_template_id,
            }
            resp = requests.post(
                f"{SUPABASE_URL}/rest/v1/custom_templates",
                headers=_headers(),
                json=row,
                timeout=10,
            )
            if resp.status_code not in (200, 201):
                logger.warning(f"Failed to save custom template: {resp.status_code}")
        except Exception as e:
            logger.warning(f"Custom template save failed: {e}")

    return ft


def load_custom_templates(user_id: str) -> List[FormatTemplate]:
    """Load all custom templates for a user from Supabase."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []

    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/custom_templates",
            headers=_headers(),
            params={"user_id": f"eq.{user_id}", "select": "template_config"},
            timeout=10,
        )
        if resp.status_code == 200:
            rows = resp.json()
            templates = []
            for row in rows:
                config = row.get("template_config", {})
                if config:
                    try:
                        templates.append(FormatTemplate(**config))
                    except Exception:
                        continue
            return templates
    except Exception as e:
        logger.warning(f"Failed to load custom templates: {e}")

    return []


def delete_custom_template(user_id: str, template_id: str) -> bool:
    """Delete a custom template."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False

    try:
        resp = requests.delete(
            f"{SUPABASE_URL}/rest/v1/custom_templates",
            headers=_headers(),
            params={"user_id": f"eq.{user_id}", "template_id": f"eq.{template_id}"},
            timeout=10,
        )
        return resp.status_code in (200, 204)
    except Exception as e:
        logger.warning(f"Failed to delete custom template: {e}")
        return False


def preview_template_config(template_config: Dict[str, Any]) -> Dict[str, Any]:
    """Preview a template configuration by generating a sample DOCX structure description."""
    try:
        ft = FormatTemplate(
            id="preview",
            name=template_config.get("name", "Preview"),
            description="Preview configuration",
            body_font=FontConfig(**template_config.get("body_font", {})),
            title_font=FontConfig(**template_config.get("title_font", {})),
            margins=MarginConfig(**template_config.get("margins", {})),
            headings=[HeadingConfig(**h) for h in template_config.get("headings", [])],
            column_count=template_config.get("column_count", 1),
            line_spacing=template_config.get("line_spacing", 1.0),
            two_column=template_config.get("two_column", False),
        )
        return {
            "valid": True,
            "template": ft.model_dump(),
            "summary": {
                "body_font": f"{ft.body_font.name} {ft.body_font.size_pt}pt",
                "title_font": f"{ft.title_font.name} {ft.title_font.size_pt}pt",
                "margins": f"top={ft.margins.top_inches}\" bottom={ft.margins.bottom_inches}\" left={ft.margins.left_inches}\" right={ft.margins.right_inches}\"",
                "columns": ft.column_count,
                "line_spacing": ft.line_spacing,
            },
        }
    except Exception as e:
        return {"valid": False, "error": str(e)}
