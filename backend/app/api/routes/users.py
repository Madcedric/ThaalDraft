from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from app.services.auth import get_current_user
from app.services import storage_service
import os
import time
import requests

router = APIRouter()

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def _headers():
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("id")
    if not SUPABASE_URL or not SUPABASE_KEY:
        return {"id": user_id, "email": current_user.get("email", ""), "display_name": "", "avatar_url": ""}

    try:
        resp = requests.get(
            f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}&select=*",
            headers=_headers(),
            timeout=10,
        )
        if resp.status_code == 200 and resp.json():
            row = resp.json()[0]
            return {
                "id": row.get("id"),
                "email": row.get("email", ""),
                "display_name": row.get("display_name", ""),
                "avatar_url": row.get("avatar_url", ""),
                "created_at": row.get("created_at", ""),
            }
    except Exception:
        pass

    return {"id": user_id, "email": current_user.get("email", ""), "display_name": "", "avatar_url": ""}


@router.put("/profile")
async def update_profile(
    display_name: str = "",
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("id")
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise HTTPException(status_code=503, detail="Database not configured")

    try:
        resp = requests.patch(
            f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}",
            headers={**_headers(), "Prefer": "return=representation"},
            json={"display_name": display_name},
            timeout=10,
        )
        if resp.status_code in (200, 204):
            return {"message": "Profile updated"}
        raise HTTPException(status_code=500, detail=f"Update failed: {resp.status_code}")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/profile/avatar")
async def upload_avatar(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    user_id = current_user.get("id")

    ext = os.path.splitext(file.filename or "avatar.jpg")[1] or ".jpg"
    dest_path = f"avatars/{user_id}{ext}"

    tmp_dir = "uploads"
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"avatar_{user_id}{ext}")

    content = await file.read()
    with open(tmp_path, "wb") as f:
        f.write(content)

    storage_path = storage_service.upload_file_to_supabase(tmp_path, dest_path)

    try:
        os.remove(tmp_path)
    except Exception:
        pass

    if not storage_path:
        raise HTTPException(status_code=500, detail="Failed to upload avatar to storage")

    avatar_url = storage_service.get_storage_url(storage_path)

    if SUPABASE_URL and SUPABASE_KEY:
        try:
            requests.patch(
                f"{SUPABASE_URL}/rest/v1/users?id=eq.{user_id}",
                headers=_headers(),
                json={"avatar_url": avatar_url},
                timeout=10,
            )
        except Exception:
            pass

    return {"avatar_url": avatar_url}
