import os
import uuid
import time
import asyncio
import requests
from typing import Dict, Optional

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

_timeout = 10


def _supabase_headers(include_return: bool = False) -> Dict:
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    if include_return:
        h["Content-Type"] = "application/json"
        h["Prefer"] = "return=representation"
    return h


def ensure_user_exists(user_id: str, email: str = "") -> bool:
    """Ensure a user row exists in Supabase. Creates it if missing (idempotent).

    Returns True if user exists or was created. False on failure.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        return True

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/users"

    # Check if user exists
    try:
        r = requests.get(
            f"{url}?id=eq.{user_id}&select=id",
            headers=_supabase_headers(),
            timeout=10,
        )
        if r.status_code == 200 and r.json():
            return True
    except Exception as e:
        print(f"WARN: ensure_user_exists check failed: {e}")

    # Insert user (upsert to avoid duplicate errors)
    try:
        r = requests.post(
            url,
            json=[{"id": user_id, "email": email or f"{user_id}@placeholder.com", "provider": "firebase"}],
            headers={**_supabase_headers(include_return=True), "Prefer": "resolution=merge-duplicates,return=representation"},
            timeout=10,
        )
        if r.status_code in (200, 201):
            print(f"INFO: Created user {user_id} in users table")
            return True
        print(f"WARN: ensure_user_exists insert failed: {r.status_code} {r.text[:200]}")
    except Exception as e:
        print(f"ERROR: ensure_user_exists insert exception: {e}")

    return False


def create_document_record(doc: Dict) -> Dict:
    """Creates a document row in Supabase via REST. Returns the created representation.

    Always returns a dict with an 'id' field.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — document record not persisted.")
        doc.setdefault("id", "local-" + str(uuid.uuid4())[:8])
        return doc

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents"
    headers = _supabase_headers(include_return=True)

    try:
        print(f"DB INSERT: user_id={doc.get('user_id')}, filename={doc.get('filename')}")
        res = requests.post(url, json=[doc], headers=headers, timeout=15)
        print(f"DB INSERT RESPONSE: status={res.status_code}")
        if res.status_code in (200, 201):
            data = res.json()
            if isinstance(data, list) and data:
                created = data[0]
                print(f"DB INSERT SUCCESS: id={created.get('id')}")
                return created
        print(f"DB INSERT FAILED: {res.status_code} {res.text[:300]}")
    except Exception as e:
        print(f"DB INSERT EXCEPTION: {e}")

    # Always return a dict with an id — even if Supabase insert failed
    fallback_id = str(uuid.uuid4())
    doc.setdefault("id", fallback_id)
    print(f"DB INSERT FALLBACK: id={fallback_id} (row NOT in database)")
    return doc


def get_document(document_id: str) -> Optional[Dict]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — cannot fetch document.")
        return None

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents?id=eq.{document_id}&select=*"
    headers = _supabase_headers()
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and data:
                print(f"DB GET: document_id={document_id} FOUND, user_id={data[0].get('user_id')}")
                return data[0]
            print(f"DB GET: document_id={document_id} NOT FOUND (empty result)")
            return None
        print(f"DB GET FAILED: {res.status_code} {res.text[:200]}")
        return None
    except Exception as e:
        print(f"DB GET EXCEPTION: {e}")
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
        res = requests.delete(url, headers=headers, timeout=_timeout)
        if res.status_code in (200, 204):
            return True
        print(f"WARN: delete_document failed: {res.status_code} {res.text}")
        return False
    except Exception as e:
        print(f"ERROR: delete_document exception: {e}")
        return False


async def get_document_async(document_id: str) -> Optional[Dict]:
    """Async version of get_document using thread pool."""
    return await asyncio.to_thread(get_document, document_id)


async def update_document_async(document_id: str, patch: Dict) -> Optional[Dict]:
    """Async version of update_document using thread pool."""
    return await asyncio.to_thread(update_document, document_id, patch)


async def create_document_record_async(doc: Dict) -> Dict:
    """Async version of create_document_record using thread pool."""
    return await asyncio.to_thread(create_document_record, doc)


async def list_documents_for_user_async(user_id: str, limit: int = 50, offset: int = 0) -> list:
    """Async version of list_documents_for_user using thread pool."""
    return await asyncio.to_thread(list_documents_for_user, user_id, limit, offset)
