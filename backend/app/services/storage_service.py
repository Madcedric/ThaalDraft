import os
import re
import requests
from typing import Optional

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
SUPABASE_BUCKET = os.environ.get("SUPABASE_STORAGE_BUCKET", "manuscripts")


def _sanitize_storage_key(dest_path: str) -> str:
    """Sanitize a storage key for Supabase Storage (no special chars, spaces → underscores)."""
    name = os.path.basename(dest_path)
    ext = os.path.splitext(name)[1].lower()
    base = os.path.splitext(name)[0]
    base = re.sub(r'[^\w\-]', '_', base)
    base = re.sub(r'_+', '_', base).strip('_')
    if not base:
        base = "file"
    parent = os.path.dirname(dest_path)
    sanitized = f"{base}{ext}"
    if parent:
        sanitized = f"{parent}/{sanitized}"
    return sanitized


def upload_file_to_supabase(local_path: str, dest_path: str) -> Optional[str]:
    """Uploads a file to Supabase Storage using the service role key.

    Returns the storage path (bucket/object) on success, or None on failure / not configured.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase storage not configured; skipping upload.")
        return None

    safe_dest = _sanitize_storage_key(dest_path)
    url = f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/{SUPABASE_BUCKET}/{safe_dest}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_KEY}",
    }

    try:
        with open(local_path, "rb") as f:
            res = requests.put(url, data=f, headers=headers, timeout=30)
        if res.status_code in (200, 201, 204):
            return f"{SUPABASE_BUCKET}/{safe_dest}"
        else:
            print(f"WARN: Supabase storage upload failed: {res.status_code} {res.text}")
            return None
    except Exception as e:
        print(f"ERROR: Supabase storage upload exception: {e}")
        return None


def get_storage_url(storage_path: str) -> str:
    """Return a URL to access the storage object when using Supabase public bucket.

    For private buckets, presigned URLs should be generated server-side.
    """
    if not SUPABASE_URL:
        return storage_path
    return f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/public/{storage_path}"


def download_file_from_supabase(storage_path: str, dest_path: str) -> bool:
    """Download an object from Supabase Storage to `dest_path` using the service role key.

    Returns True on success, False otherwise.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase storage not configured; cannot download file.")
        return False

    # storage_path expected in the form 'bucket/object...'
    # If caller provides 'bucket/object', split; otherwise use default bucket
    parts = storage_path.split("/", 1)
    if len(parts) == 2:
        bucket, obj = parts[0], parts[1]
    else:
        bucket = SUPABASE_BUCKET
        obj = storage_path

    url = f"{SUPABASE_URL.rstrip('/')}/storage/v1/object/{bucket}/{obj}"
    headers = {"Authorization": f"Bearer {SUPABASE_KEY}"}

    try:
        with requests.get(url, headers=headers, stream=True, timeout=60) as r:
            if r.status_code != 200:
                print(f"WARN: download failed: {r.status_code} {r.text}")
                return False
            os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
        return True
    except Exception as e:
        print(f"ERROR: download exception: {e}")
        return False
