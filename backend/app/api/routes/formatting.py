from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from app.services.formatting.engine_v2 import format_manuscript, validate_manuscript, TEMPLATE_CONFIGS
from app.services.formatting.schema import ExportType, FormattedOutput, FormatValidation
from app.services.manuscript.model import manuscript_from_dict
from app.services import document_service
from app.api.routes.auth import get_current_user
import os

router = APIRouter()


class FormatRequestV2(BaseModel):
    template_id: str
    export_type: ExportType = ExportType.DOCX
    validate_only: bool = False


@router.get("/formatting/templates")
async def list_formatting_templates():
    """List all available formatting templates."""
    templates = []
    for tid, config in TEMPLATE_CONFIGS.items():
        templates.append({
            "id": tid,
            "name": config.name,
            "body_font": config.body_font,
            "body_size": config.body_size,
            "two_column": config.two_column,
            "requires_keywords": config.requires_keywords,
        })
    return {"templates": templates}


@router.get("/formatting/templates/{template_id}")
async def get_formatting_template(template_id: str):
    """Get a specific formatting template."""
    config = TEMPLATE_CONFIGS.get(template_id)
    if not config:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return {
        "id": template_id,
        "name": config.name,
        "body_font": config.body_font,
        "body_size": config.body_size,
        "two_column": config.two_column,
        "requires_keywords": config.requires_keywords,
    }


@router.post("/{document_id}/formatting/preview")
async def preview_formatting(
    document_id: str,
    request: FormatRequestV2,
    current_user: dict = Depends(get_current_user),
):
    """Preview formatting validation without generating output."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        structured_data = doc.get("parsed_json") or {}
        if not structured_data:
            raise HTTPException(status_code=400, detail="Document must be structured before formatting")

        manuscript_data = structured_data.get("manuscript_model") or structured_data
        manuscript = manuscript_from_dict(manuscript_data)

        validation = validate_manuscript(manuscript, request.template_id)

        return {
            "document_id": document_id,
            "template_id": request.template_id,
            "validation": validation,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/formatting/format")
async def format_document_endpoint(
    document_id: str,
    request: FormatRequestV2,
    current_user: dict = Depends(get_current_user),
):
    """Format a document using the specified template."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        structured_data = doc.get("parsed_json") or {}
        if not structured_data:
            raise HTTPException(status_code=400, detail="Document must be structured before formatting")

        manuscript_data = structured_data.get("manuscript_model") or structured_data
        manuscript = manuscript_from_dict(manuscript_data)

        output_path = format_manuscript(manuscript, request.template_id)

        file_size = os.path.getsize(output_path) if os.path.exists(output_path) else 0

        return {
            "document_id": document_id,
            "output": {
                "file_path": output_path,
                "file_size": file_size,
                "template_id": request.template_id,
                "export_type": request.export_type.value,
            },
            "status": "completed",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/formatting")
async def get_document_formatting(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get formatting status for a document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        status = doc.get("status")
        return {
            "document_id": document_id,
            "status": status,
            "message": "Document is formatted" if status == "formatted" else "Not formatted yet",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
