import os
import requests
from typing import Dict

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def upsert_user(user: Dict) -> Dict:
    """Upserts a user into Supabase `users` table via the REST endpoint.

    If `SUPABASE_URL` / `SUPABASE_KEY` are not configured, this becomes a no-op and returns the input user.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        # Running in dev mode or Supabase not configured.
        print("INFO: Supabase not configured — skipping user persistence.")
        return user

    url = f"{SUPABASE_URL.rstrip('/')}/rest/v1/users?on_conflict=id"
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        # Ask Supabase to merge duplicates (upsert) and return the representation
        "Prefer": "return=representation, resolution=merge-duplicates"
    }

    try:
        # The Supabase REST API expects an array for inserts
        res = requests.post(url, json=[user], headers=headers, timeout=5)
        if res.status_code in (200, 201):
            data = res.json()
            # Return the representation of the upserted user (first element)
            if isinstance(data, list) and data:
                return data[0]
            return user
        else:
            print(f"WARN: Supabase user upsert failed: {res.status_code} {res.text}")
            return user
    except Exception as e:
        print(f"ERROR: Supabase upsert exception: {e}")
        return user
