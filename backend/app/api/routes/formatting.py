from fastapi import APIRouter, HTTPException, Depends
from app.services.formatting import (
    FormatRequest,
    FormatResponse,
    FormattedOutput,
    ExportType,
    format_document,
    get_all_templates,
    get_template,
)
from app.services import document_service
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.get("/formatting/templates")
async def list_formatting_templates():
    """List all available formatting templates."""
    templates = get_all_templates()
    return {"templates": [t.model_dump() for t in templates]}


@router.get("/formatting/templates/{template_id}")
async def get_formatting_template(template_id: str):
    """Get a specific formatting template."""
    template = get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")
    return template.model_dump()


@router.post("/{document_id}/formatting/preview")
async def preview_formatting(
    document_id: str,
    request: FormatRequest,
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
            raise HTTPException(
                status_code=400,
                detail="Document must be structured before formatting",
            )

        from app.services.formatting.engine import _validate_structured_data
        from app.services.formatting.templates import get_template as get_tpl

        template = get_tpl(request.template_id)
        if not template:
            raise HTTPException(status_code=404, detail=f"Template '{request.template_id}' not found")

        validation = _validate_structured_data(structured_data, template)

        return {
            "document_id": document_id,
            "template_id": request.template_id,
            "validation": validation.model_dump(),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/formatting/format", response_model=FormatResponse)
async def format_document_endpoint(
    document_id: str,
    request: FormatRequest,
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
            raise HTTPException(
                status_code=400,
                detail="Document must be structured before formatting",
            )

        output = format_document(
            document_id=document_id,
            structured_data=structured_data,
            template_id=request.template_id,
            export_type=request.export_type,
        )

        document_service.update_document(document_id, {"status": "formatted"})

        return FormatResponse(
            document_id=document_id,
            output=output,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/formatting")
async def get_document_formatting(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get existing formatting output for a document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        status = doc.get("status")
        if status != "formatted":
            return {
                "document_id": document_id,
                "status": status,
                "message": "Document has not been formatted yet",
            }

        return {
            "document_id": document_id,
            "status": status,
            "message": "Document is formatted",
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
