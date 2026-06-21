import os
import requests
from typing import Dict, Optional

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def create_job(job: Dict) -> Dict:
    """Creates a job row in Supabase. If not configured, returns the job as-is with an id placeholder."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — job record not persisted.")
        job.setdefault("id", "local-job-" + job.get("type", "unknown"))
        return job

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/jobs"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }

    try:
        res = requests.post(url, json=[job], headers=headers, timeout=10)
        if res.status_code in (200, 201):
            data = res.json()
            if isinstance(data, list) and data:
                return data[0]
        print(f"WARN: create_job failed: {res.status_code} {res.text}")
        return job
    except Exception as e:
        print(f"ERROR: create_job exception: {e}")
        return job


def fetch_pending_job(job_type: str | None = None) -> Optional[Dict]:
    """Fetch a single pending job (FIFO). Optionally filter by job_type."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — no jobs to fetch.")
        return None

    q = "status=eq.pending"
    if job_type:
        q += f"&type=eq.{job_type}"

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/jobs?{q}&order=created_at.asc&limit=1"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            if isinstance(data, list) and data:
                return data[0]
        return None
    except Exception as e:
        print(f"ERROR: fetch_pending_job exception: {e}")
        return None


def update_job(job_id: str, patch: Dict) -> Optional[Dict]:
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — update_job is a no-op.")
        return None

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/jobs?id=eq.{job_id}"
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
        print(f"WARN: update_job failed: {res.status_code} {res.text}")
        return None
    except Exception as e:
        print(f"ERROR: update_job exception: {e}")
        return None


def list_jobs_for_document(document_id: str, limit: int = 50) -> list:
    """Return jobs for a given document, newest first. Falls back to empty list when Supabase not configured."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("INFO: Supabase not configured — cannot list jobs for document.")
        return []

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/jobs?document_id=eq.{document_id}&select=*&order=created_at.desc&limit={limit}"
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    try:
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            return res.json()
        print(f"WARN: list_jobs_for_document failed: {res.status_code} {res.text}")
        return []
    except Exception as e:
        print(f"ERROR: list_jobs_for_document exception: {e}")
        return []
