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
    """Ensure a user row exists in Supabase. Creates it if missing (idempotent)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return True

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/users"

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
        raise Exception(f"Failed to create user in database. Status: {r.status_code}")
    except Exception as e:
        print(f"ERROR: ensure_user_exists insert exception: {e}")
        raise Exception(f"Database user synchronization failed: {e}")


def create_document_record(doc: Dict) -> Dict:
    """Creates a document row and normalized related records (manuscripts, sections, references)."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — document record not persisted.")
        doc.setdefault("id", "local-" + str(uuid.uuid4())[:8])
        return doc

    headers = _supabase_headers(include_return=True)
    
    # Extract parsed_json from payload for normalized insertion
    parsed_json = doc.pop("parsed_json", {})
    doc.setdefault("mode", "reconstruction")
    # Include parsed_json in the insert so get_document can return it
    doc["parsed_json"] = parsed_json
    
    doc_url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents"
    try:
        res = requests.post(doc_url, json=[doc], headers=headers, timeout=15)
        if res.status_code not in (200, 201):
            raise Exception(f"Database insert failed with status {res.status_code}: {res.text[:300]}")
            
        created = res.json()[0]
        doc_id = created.get("id")
        
        # Insert Normalized Records
        if parsed_json:
            manuscript_payload = {
                "document_id": doc_id,
                "title": parsed_json.get("title", "Untitled Manuscript"),
                "abstract": parsed_json.get("abstract", ""),
                "authors": parsed_json.get("authors", [])
            }
            m_url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/manuscripts"
            m_res = requests.post(m_url, json=[manuscript_payload], headers=headers, timeout=10)
            
            if m_res.status_code in (200, 201):
                manuscript_id = m_res.json()[0].get("id")
                
                # Insert Sections
                sections = parsed_json.get("sections", [])
                if sections:
                    s_payload = []
                    for idx, sec in enumerate(sections):
                        if isinstance(sec, dict):
                            s_payload.append({
                                "manuscript_id": manuscript_id,
                                "heading": sec.get("heading", ""),
                                "label": sec.get("heading", f"Section {idx+1}"),
                                "content": sec.get("content", ""),
                                "section_order": idx,
                                "level": sec.get("level", 1)
                            })
                    if s_payload:
                        s_url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/sections"
                        requests.post(s_url, json=s_payload, headers=headers, timeout=10)
                
                # Insert References
                references = parsed_json.get("references", [])
                if references:
                    r_payload = []
                    for ref in references:
                        if isinstance(ref, str):
                            r_payload.append({"manuscript_id": manuscript_id, "raw_text": ref})
                        elif isinstance(ref, dict):
                            r_payload.append({"manuscript_id": manuscript_id, "raw_text": ref.get("raw_text", ""), "doi": ref.get("doi")})
                    if r_payload:
                        r_url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/references_table"
                        requests.post(r_url, json=r_payload, headers=headers, timeout=10)

        # Repopulate for backward compatibility in backend flow
        created["parsed_json"] = parsed_json
        return created

    except Exception as e:
        print(f"DB INSERT EXCEPTION: {e}")
        raise Exception(f"Failed to create document record: {e}")


def get_document(document_id: str) -> Optional[Dict]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    headers = _supabase_headers()
    doc_url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents?id=eq.{document_id}&select=*"
    
    try:
        res = requests.get(doc_url, headers=headers, timeout=10)
        if res.status_code == 200 and res.json():
            doc = res.json()[0]
            
            # Use parsed_json directly from the document row
            parsed_json = doc.get("parsed_json") or {}
            
            # If parsed_json is empty, try to rebuild from normalized tables
            if not parsed_json.get("sections"):
                m_url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/manuscripts?document_id=eq.{document_id}&select=*"
                m_res = requests.get(m_url, headers=headers, timeout=10)
                if m_res.status_code == 200 and m_res.json():
                    manuscript = m_res.json()[0]
                    manuscript_id = manuscript.get("id")
                    
                    parsed_json["title"] = manuscript.get("title")
                    parsed_json["abstract"] = manuscript.get("abstract")
                    parsed_json["authors"] = manuscript.get("authors") or []
                    
                    s_url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/sections?manuscript_id=eq.{manuscript_id}&order=section_order.asc&select=*"
                    s_res = requests.get(s_url, headers=headers, timeout=10)
                    if s_res.status_code == 200:
                        parsed_json["sections"] = s_res.json()
                        
                    r_url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/references_table?manuscript_id=eq.{manuscript_id}&select=*"
                    r_res = requests.get(r_url, headers=headers, timeout=10)
                    if r_res.status_code == 200:
                        parsed_json["references"] = [r.get("raw_text") for r in r_res.json()]
            
            doc["parsed_json"] = parsed_json
            return doc
            
        return None
    except Exception as e:
        print(f"DB GET EXCEPTION: {e}")
        return None


def update_document(document_id: str, patch: Dict) -> Optional[Dict]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents?id=eq.{document_id}"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    # Intercept parsed_json if it's being updated
    parsed_json = patch.pop("parsed_json", None)
    
    try:
        if patch:
            res = requests.patch(url, json=patch, headers=headers, timeout=10)
            if res.status_code not in (200, 204):
                print(f"WARN: update_document failed: {res.status_code} {res.text}")
                return None
        
        # In Phase 1, we just fetch and return the updated document. Full deep-updates for normalized tables 
        # (if sections/references change) will be implemented in subsequent phases.
        return get_document(document_id)
    except Exception as e:
        print(f"ERROR: update_document exception: {e}")
        return None


def list_documents_texts(exclude_document_id: str = None, limit: int = 50) -> list:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []

    q = f"select=id&limit={limit}"
    if exclude_document_id:
        q = f"select=id&id=not.eq.{exclude_document_id}&limit={limit}"

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents?{q}"
    headers = _supabase_headers()
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            out = []
            for r in res.json():
                pid = r.get("id")
                # Rebuild text using get_document for backward compatibility during Phase 1
                doc = get_document(pid)
                if doc:
                    parsed = doc.get("parsed_json", {})
                    parts = []
                    if parsed.get("title"): parts.append(parsed.get("title"))
                    if parsed.get("abstract"): parts.append(parsed.get("abstract"))
                    for s in parsed.get("sections", []):
                        parts.append(s.get("heading", ""))
                        parts.append(s.get("content", ""))
                    combined = "\\n".join([p for p in parts if p])
                    out.append({"id": pid, "text": combined})
            return out
        return []
    except Exception as e:
        print(f"ERROR: list_documents_texts exception: {e}")
        return []


def list_documents_for_user(user_id: str, limit: int = 50, offset: int = 0) -> list:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents?user_id=eq.{user_id}&select=*&order=created_at.desc&limit={limit}&offset={offset}"
    headers = _supabase_headers()
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        return []
    except Exception as e:
        print(f"ERROR: list_documents_for_user exception: {e}")
        return []


def delete_document(document_id: str) -> bool:
    if not SUPABASE_URL or not SUPABASE_KEY:
        return False

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/documents?id=eq.{document_id}"
    headers = _supabase_headers()
    try:
        res = requests.delete(url, headers=headers, timeout=_timeout)
        return res.status_code in (200, 204)
    except Exception as e:
        print(f"ERROR: delete_document exception: {e}")
        return False


async def get_document_async(document_id: str) -> Optional[Dict]:
    return await asyncio.to_thread(get_document, document_id)


async def update_document_async(document_id: str, patch: Dict) -> Optional[Dict]:
    return await asyncio.to_thread(update_document, document_id, patch)


async def create_document_record_async(doc: Dict) -> Dict:
    return await asyncio.to_thread(create_document_record, doc)


async def list_documents_for_user_async(user_id: str, limit: int = 50, offset: int = 0) -> list:
    return await asyncio.to_thread(list_documents_for_user, user_id, limit, offset)
