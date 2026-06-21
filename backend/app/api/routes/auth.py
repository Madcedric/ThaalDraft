from fastapi import APIRouter, Depends, HTTPException
from app.services.auth import get_current_user, FIREBASE_PROJECT_ID
from app.services.user_service import upsert_user
from pydantic import BaseModel

router = APIRouter()


class LoginRequest(BaseModel):
    username: str | None = None
    password: str | None = None


@router.post("/login")
def login(payload: LoginRequest):
    """Simple development login endpoint.

    When `FIREBASE_PROJECT_ID` is not configured this will return a mock
    bearer token usable by the backend's `get_current_user` (tokens that
    start with "mock-" are accepted by the auth service). In production
    environments when Firebase is configured, this endpoint is disabled
    to avoid exposing unsafe auth paths.
    """
    if FIREBASE_PROJECT_ID:
        raise HTTPException(status_code=501, detail="Login via backend is disabled when Firebase is configured")

    # Basic acceptance for local/dev testing — no real verification.
    username = payload.username or "developer"
    return {"access_token": f"mock-{username}", "token_type": "bearer"}


@router.get("/me")
def me(current_user: dict = Depends(get_current_user)):
    """Returns the authenticated user's profile and ensures a minimal persistence record exists.

    This endpoint is safe to call from the frontend after sign-in to sync the user record.
    """
    # Attempt to persist the user record into Supabase (no-op when not configured)
    user_payload = {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "name": current_user.get("name") or None,
        "provider": current_user.get("provider") or "firebase"
    }
    persisted = upsert_user(user_payload)
    return {"user": persisted}
