from fastapi import APIRouter

router = APIRouter()

@router.get("/", tags=["Health"])
def liveness():
    return {"status": "ok", "service": "ThaalDraft API"}

@router.get("/ready", tags=["Health"])
def readiness():
    # In future, perform DB, storage, and external service checks here
    return {"ready": True}
