"""Manuscript Persistence Layer — V2.

Handles reading/writing StructuredManuscript to/from Supabase normalized tables:
- manuscripts (canonical_json)
- sections
- figures
- tables
- references_table
- doi_records

Also supports backward-compatible JSONB storage in documents.parsed_json.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

import requests

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


# ─── Save Canonical Manuscript ────────────────────────────────────────────────


def save_manuscript(document_id: str, manuscript_dict: Dict[str, Any]) -> bool:
    """Save a StructuredManuscript to Supabase normalized tables.

    Args:
        document_id: The document ID (FK to documents table).
        manuscript_dict: Serialized StructuredManuscript dict.

    Returns:
        True if saved successfully, False otherwise.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("Supabase not configured, skipping manuscript save")
        return False

    try:
        # 1. Upsert manuscripts table
        manuscript_row = {
            "document_id": document_id,
            "title": manuscript_dict.get("title", ""),
            "abstract": manuscript_dict.get("abstract", ""),
            "keywords": manuscript_dict.get("keywords", []),
            "canonical_json": manuscript_dict,
            "word_count": manuscript_dict.get("word_count", 0),
            "section_count": manuscript_dict.get("section_count", 0),
            "reference_count": manuscript_dict.get("reference_count", 0),
            "confidence_score": _compute_confidence(manuscript_dict),
        }

        resp = requests.post(
            f"{SUPABASE_URL}/rest/v1/manuscripts",
            headers=_headers(),
            json=manuscript_row,
            params={"on_conflict": "document_id"},
            timeout=10,
        )
        if resp.status_code not in (200, 201):
            logger.error(f"Failed to save manuscript: {resp.status_code} {resp.text[:200]}")
            return False

        # Get manuscript_id
        rows = resp.json()
        if not rows:
            logger.error("No manuscript row returned")
            return False
        manuscript_id = rows[0]["id"]

        # 2. Delete existing child records
        for table in ["sections", "figures", "tables", "references_table"]:
            requests.delete(
                f"{SUPABASE_URL}/rest/v1/{table}",
                headers=_headers(),
                params={"manuscript_id": f"eq.{manuscript_id}"},
                timeout=10,
            )

        # 3. Insert sections
        sections = manuscript_dict.get("sections") or []
        if sections:
            section_rows = []
            for i, sec in enumerate(sections):
                section_rows.append({
                    "manuscript_id": manuscript_id,
                    "heading": sec.get("heading", ""),
                    "label": sec.get("label", "other"),
                    "section_order": i,
                    "level": sec.get("level", 1),
                    "confidence": sec.get("confidence", 0.0),
                    "content": sec.get("content", ""),
                })
            requests.post(
                f"{SUPABASE_URL}/rest/v1/sections",
                headers=_headers(),
                json=section_rows,
                timeout=10,
            )

        # 4. Insert figures
        figures = manuscript_dict.get("figures") or []
        if figures:
            fig_rows = []
            for fig in figures:
                fig_rows.append({
                    "manuscript_id": manuscript_id,
                    "caption": fig.get("caption", ""),
                    "image_path": fig.get("image_path"),
                    "extracted_from": fig.get("position"),
                })
            requests.post(
                f"{SUPABASE_URL}/rest/v1/figures",
                headers=_headers(),
                json=fig_rows,
                timeout=10,
            )

        # 5. Insert tables
        tables = manuscript_dict.get("tables") or []
        if tables:
            tbl_rows = []
            for tbl in tables:
                tbl_rows.append({
                    "manuscript_id": manuscript_id,
                    "caption": tbl.get("caption", ""),
                    "table_data": tbl.get("rows", []),
                    "extracted_from": tbl.get("position"),
                })
            requests.post(
                f"{SUPABASE_URL}/rest/v1/tables",
                headers=_headers(),
                json=tbl_rows,
                timeout=10,
            )

        # 6. Insert references
        refs = manuscript_dict.get("references") or []
        if refs:
            ref_rows = []
            for ref in refs:
                ref_rows.append({
                    "manuscript_id": manuscript_id,
                    "ref_index": ref.get("index", 0),
                    "raw_text": ref.get("raw_text", ""),
                    "authors": ref.get("authors", []),
                    "title": ref.get("title"),
                    "journal": ref.get("journal"),
                    "year": ref.get("year"),
                    "doi": ref.get("doi"),
                    "url": ref.get("url"),
                })
            requests.post(
                f"{SUPABASE_URL}/rest/v1/references_table",
                headers=_headers(),
                json=ref_rows,
                timeout=10,
            )

        logger.info(f"Saved manuscript {manuscript_id} for document {document_id}")
        return True

    except Exception as e:
        logger.error(f"Error saving manuscript: {e}")
        return False


# ─── Load Canonical Manuscript ────────────────────────────────────────────────


def load_manuscript(document_id: str) -> Optional[Dict[str, Any]]:
    """Load a StructuredManuscript from Supabase.

    Tries normalized tables first, falls back to documents.parsed_json.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    try:
        # Try manuscripts table
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/manuscripts",
            headers=_headers(),
            params={"document_id": f"eq.{document_id}", "select": "canonical_json"},
            timeout=10,
        )
        if resp.status_code == 200:
            rows = resp.json()
            if rows and rows[0].get("canonical_json"):
                return rows[0]["canonical_json"]

        # Fallback: try documents.parsed_json
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/documents",
            headers=_headers(),
            params={"id": f"eq.{document_id}", "select": "parsed_json"},
            timeout=10,
        )
        if resp.status_code == 200:
            rows = resp.json()
            if rows:
                parsed = rows[0].get("parsed_json") or {}
                manuscript_model = parsed.get("manuscript_model")
                if manuscript_model:
                    return manuscript_model
                return parsed

    except Exception as e:
        logger.error(f"Error loading manuscript: {e}")

    return None


# ─── Helpers ──────────────────────────────────────────────────────────────────


def _compute_confidence(manuscript_dict: Dict[str, Any]) -> float:
    """Compute a confidence score based on manuscript completeness."""
    score = 0.0
    if manuscript_dict.get("title"):
        score += 15
    if manuscript_dict.get("abstract"):
        score += 15
    if manuscript_dict.get("authors"):
        score += 10
    sections = manuscript_dict.get("sections") or []
    if len(sections) >= 3:
        score += 20
    if len(sections) >= 5:
        score += 10
    refs = manuscript_dict.get("references") or []
    if len(refs) >= 5:
        score += 15
    if len(refs) >= 10:
        score += 10
    if manuscript_dict.get("keywords"):
        score += 5
    return min(score, 100.0)
