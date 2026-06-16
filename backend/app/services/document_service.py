import os
import requests
from typing import Dict, Optional

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def create_document_record(doc: Dict) -> Dict:
    """Creates a document row in Supabase via REST. Returns the created representation.

    If Supabase is not configured, returns the input dict with a generated id placeholder.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — document record not persisted.")
        # Provide a lightweight id placeholder
        doc.setdefault("id", "local-" + (doc.get("filename", "unknown")))
        return doc

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    try:
        res = requests.post(url, json=[doc], headers=headers, timeout=10)
        if res.status_code in (200, 201):
            data = res.json()
            if isinstance(data, list) and data:
                return data[0]
        print(f"WARN: create_document_record failed: {res.status_code} {res.text}")
        return doc
    except Exception as e:
        print(f"ERROR: create_document_record exception: {e}")
        return doc


def get_document(document_id: str) -> Optional[Dict]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — cannot fetch document.")
        return None

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents?id=eq.{document_id}&select=*"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and data:
                return data[0]
        print(f"WARN: get_document failed: {res.status_code} {res.text}")
        return None
    except Exception as e:
        print(f"ERROR: get_document exception: {e}")
        return None


def update_document(document_id: str, patch: Dict) -> Optional[Dict]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — update_document is a no-op.")
        return None

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents?id=eq.{document_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    try:
        res = requests.patch(url, json=patch, headers=headers, timeout=10)
        if res.status_code in (200, 204):
            data = res.json()
            if isinstance(data, list) and data:
                return data[0]
        print(f"WARN: update_document failed: {res.status_code} {res.text}")
        return None
    except Exception as e:
        print(f"ERROR: update_document exception: {e}")
        return None


def list_documents_texts(exclude_document_id: str = None, limit: int = 50) -> list:
    """Return a list of other documents with combined text (title + abstract + sections).

    Falls back to empty list when Supabase not configured.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — cannot list documents for comparison.")
        return []

    # Build query to select id and parsed_json where parsed_json is not null and id != exclude
    q = "select=id,parsed_json&limit=" + str(limit)
    if exclude_document_id:
        q = f"select=id,parsed_json&id=not.eq.{exclude_document_id}&limit={limit}"

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents?{q}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            out = []
            for r in data:
                pid = r.get("id")
                parsed = r.get("parsed_json") or {}
                # Build combined text
                parts = []
                if parsed.get("title"):
                    parts.append(parsed.get("title"))
                if parsed.get("abstract"):
                    parts.append(parsed.get("abstract"))
                for s in parsed.get("sections", []):
                    if isinstance(s, dict):
                        parts.append(s.get("heading", ""))
                        parts.append(s.get("content", ""))
                combined = "\n".join([p for p in parts if p])
                out.append({"id": pid, "text": combined})
            return out

        print(f"WARN: list_documents_texts failed: {res.status_code} {res.text}")
        return []
    except Exception as e:
        print(f"ERROR: list_documents_texts exception: {e}")
        return []


def list_documents_for_user(user_id: str, limit: int = 50, offset: int = 0) -> list:
    """List documents for a specific user."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — cannot list documents.")
        return []

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents?user_id=eq.{user_id}&select=*&order=created_at.desc&limit={limit}&offset={offset}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        print(f"WARN: list_documents_for_user failed: {res.status_code} {res.text}")
        return []
    except Exception as e:
        print(f"ERROR: list_documents_for_user exception: {e}")
        return []


def delete_document(document_id: str) -> bool:
    """Delete a document by ID."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — cannot delete document.")
        return False

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents?id=eq.{document_id}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.delete(url, headers=headers, timeout=10)
        if res.status_code in (200, 204):
            return True
        print(f"WARN: delete_document failed: {res.status_code} {res.text}")
        return False
    except Exception as e:
        print(f"ERROR: delete_document exception: {e}")
        return False
