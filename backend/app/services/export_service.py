import os
import requests
from typing import Dict

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def create_export(document_id: str, fmt: str, storage_path: str) -> Dict:
    """Creates an export row in Supabase and returns the representation.

    If Supabase not configured, returns a minimal dict.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — export not persisted.")
        return {"id": f"local-export-{document_id}", "document_id": document_id, "format": fmt, "storage_path": storage_path}

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/exports"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    payload = {"document_id": document_id, "format": fmt, "storage_path": storage_path}
    try:
        res = requests.post(url, json=[payload], headers=headers, timeout=10)
        if res.status_code in (200, 201):
            data = res.json()
            if isinstance(data, list) and data:
                return data[0]
        print(f"WARN: create_export failed: {res.status_code} {res.text}")
        return payload
    except Exception as e:
        print(f"ERROR: create_export exception: {e}")
        return payload


def get_exports_for_document(document_id: str):
    if not SUPABASE_URL or not SUPABASE_KEY:
        # fallback: scan local exports folder
        out = []
        export_dir = "exports"
        if not os.path.exists(export_dir):
            return out
        for f in os.listdir(export_dir):
            if f.startswith(str(document_id)):
                out.append({"id": f"local-{f}", "document_id": document_id, "format": os.path.splitext(f)[1].lstrip('.'), "storage_path": os.path.join(export_dir, f)})
        return out

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/exports?document_id=eq.{document_id}&select=*"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json()
        print(f"WARN: get_exports_for_document failed: {res.status_code} {res.text}")
        return []
    except Exception as e:
        print(f"ERROR: get_exports_for_document exception: {e}")
        return []


def get_export_by_id(export_id: str):
    if not SUPABASE_URL or not SUPABASE_KEY:
        # local fallback: try to find file with matching name
        export_dir = "exports"
        if os.path.exists(export_dir):
            for f in os.listdir(export_dir):
                if f.startswith(export_id) or f"local-{f}" == export_id:
                    return {"id": f"local-{f}", "storage_path": os.path.join(export_dir, f), "document_id": None, "format": os.path.splitext(f)[1].lstrip('.')}
        return None

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/exports?id=eq.{export_id}&select=*"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and data:
                return data[0]
        print(f"WARN: get_export_by_id failed: {res.status_code} {res.text}")
        return None
    except Exception as e:
        print(f"ERROR: get_export_by_id exception: {e}")
        return None
