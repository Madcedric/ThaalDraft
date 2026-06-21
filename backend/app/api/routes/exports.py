from fastapi import APIRouter, Depends, HTTPException, Body
from fastapi.responses import FileResponse
from app.services.auth import get_current_user
from app.services.export_engine import (
    export_docx, export_pdf, export_latex, export_zip_package,
    get_supported_formats, get_supported_templates,
)
from app.services.manuscript.model import manuscript_from_dict
from app.services import document_service, export_service
import os

router = APIRouter()


@router.post("/{document_id}/export")
def request_export(document_id: str, body: dict = Body(...), current_user: dict = Depends(get_current_user)):
    """Format and export a document. Returns the formatted file.

    Body params:
        template: str (default "ieee")
        format: str — "docx", "pdf", "latex", or "zip" (default "docx")
    """
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Not authorized to export this document")

    structured_data = doc.get("parsed_json") or {}
    if not structured_data:
        raise HTTPException(status_code=400, detail="Document must be structured before export")

    template = body.get("template", "ieee")
    fmt = body.get("format", "docx")

    if template not in get_supported_templates():
        raise HTTPException(status_code=400, detail=f"Unknown template: {template}")
    if fmt not in get_supported_formats():
        raise HTTPException(status_code=400, detail=f"Unknown format: {fmt}. Supported: {get_supported_formats()}")

    try:
        manuscript_data = structured_data.get("manuscript_model") or structured_data
        manuscript = manuscript_from_dict(manuscript_data)

        export_dir = f"exports/{document_id}"
        os.makedirs(export_dir, exist_ok=True)

        if fmt == "docx":
            output_path = export_docx(manuscript, template, export_dir)
            media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            ext = "docx"
        elif fmt == "pdf":
            output_path = export_pdf(manuscript, template, export_dir)
            if not output_path:
                raise HTTPException(status_code=500, detail="PDF conversion failed")
            media_type = "application/pdf"
            ext = "pdf"
        elif fmt == "latex":
            output_path = export_latex(manuscript, template, export_dir)
            media_type = "application/x-latex"
            ext = "tex"
        elif fmt == "zip":
            output_path = export_zip_package(manuscript, template, export_dir)
            media_type = "application/zip"
            ext = "zip"
        else:
            raise HTTPException(status_code=400, detail=f"Unsupported format: {fmt}")

        if output_path and os.path.exists(output_path):
            filename = f"{doc.get('filename', document_id)}_{template}.{ext}"

            export_service.create_export(
                document_id=document_id,
                fmt=ext,
                storage_path=output_path,
            )

            return FileResponse(
                path=output_path,
                filename=filename,
                media_type=media_type,
            )

        raise HTTPException(status_code=500, detail="Export generation failed")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/exports")
def list_exports(document_id: str, current_user: dict = Depends(get_current_user)):
    """List exports for a document."""
    doc = document_service.get_document(document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.get("user_id") != current_user.get("id"):
        raise HTTPException(status_code=403, detail="Not authorized")

    exports = export_service.get_exports_for_document(document_id)
    return {"exports": exports}


@router.get("/download/{export_id}")
def download_export(export_id: str, current_user: dict = Depends(get_current_user)):
    """Download a previously created export file."""
    exp = export_service.get_export_by_id(export_id)
    if not exp:
        raise HTTPException(status_code=404, detail="Export not found")

    storage_path = exp.get("storage_path")
    if storage_path and os.path.exists(storage_path):
        return FileResponse(
            path=storage_path,
            filename=os.path.basename(storage_path),
            media_type="application/octet-stream",
        )

    raise HTTPException(status_code=404, detail="Export file not available")


@router.get("/formats")
def list_export_formats():
    """List all supported export formats and templates."""
    return {
        "formats": get_supported_formats(),
        "templates": get_supported_templates(),
    }
