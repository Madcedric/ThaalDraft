from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import JSONResponse, FileResponse
from app.services.auth import get_current_user
from app.services import job_service, document_service, export_service, storage_service
import os

router = APIRouter()


@router.post("/{document_id}/export")
def request_export(document_id: str, body: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """Request an export for a document. Creates a `format` job which will be processed by workers.

    Body should include `template` (e.g., 'ieee') and `format` ('docx' or 'pdf').
    """
    # Validate document ownership (best-effort). Document service may return None when not configured.
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Not authorized to export this document")

    template = body.get("template", "ieee")
    fmt = body.get("format", "docx")

    job_payload = {"document_id": document_id, "type": "format", "status": "pending", "payload": {"template": template, "format": fmt}}
    created = job_service.create_job(job_payload)
    return JSONResponse({"job": created})


@router.get("/{document_id}/exports")
def list_exports(document_id: str, current_user: dict = Depends(get_current_user)):
    # Fetch exports for document
    exports = export_service.get_exports_for_document(document_id)
    return JSONResponse({"exports": exports})


@router.get("/download/{export_id}")
def download_export(export_id: str, current_user: dict = Depends(get_current_user)):
    exp = export_service.get_export_by_id(export_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Export not found")

    storage_path = exp.get("storage_path")
    if storage_path and storage_path.startswith("exports/"):
        # If Supabase configured, return a public URL if possible
        url = storage_service.get_storage_url(storage_path)
        # If the URL looks like a Supabase object URL, return it for client to download
        return JSONResponse({"download_url": url})

    # Fallback: if storage_path is a local path, stream the file
    if storage_path and os.path.exists(storage_path):
        return FileResponse(path=storage_path, filename=os.path.basename(storage_path), media_type="application/octet-stream")

    raise HTTPException(status_code=404, detail="Export file not available")
