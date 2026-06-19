from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
from fastapi.responses import FileResponse
from app.models.document import DocumentResponse, DocumentMeta, StructureAnalysisResponse
from app.services.document_parser import save_upload_file, parse_document, extract_metadata, get_file_extension, MIME_TYPE_MAP
from app.services.ieee_formatter import generate_ieee_docx
from app.services.auth import get_current_user
from app.services import storage_service, document_service, job_service
from app.services import plagiarism_service
from app.services import struct_service
import os
import time

router = APIRouter()


@router.post("/upload", response_model=DocumentMeta)
async def upload_document(file: UploadFile = File(...), current_user: dict = Depends(get_current_user)):
    """Upload a document for processing. Supports DOCX, PDF, LaTeX, and Markdown."""
    file_path = await save_upload_file(file)
    size = os.path.getsize(file_path)
    ext = get_file_extension(file_path)

    try:
        filename = os.path.basename(file_path)
        dest_path = f"{int(time.time())}_{filename}"
        storage_path = storage_service.upload_file_to_supabase(file_path, dest_path)

        parsed_data = parse_document(file_path)

        safe_filename = file.filename or filename or "unnamed"

        doc_payload = {
            "user_id": current_user.get("id"),
            "filename": safe_filename,
            "storage_path": storage_path,
            "status": "parsed",
            "size_bytes": size,
            "parsed_json": parsed_data,
        }
        created = document_service.create_document_record(doc_payload)

        doc_id = created.get("id")
        if not doc_id:
            raise HTTPException(status_code=500, detail="Failed to create document record: no ID returned")

        return DocumentMeta(
            id=str(doc_id),
            filename=safe_filename,
            storage_path=created.get("storage_path"),
            status=created.get("status", "parsed"),
            size_bytes=created.get("size_bytes")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parse")
async def parse_document_sync(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Parse a document synchronously and return structured JSON."""
    file_path = await save_upload_file(file)
    
    try:
        parsed = parse_document(file_path)
        metadata = extract_metadata(parsed)
        
        return {
            "filename": file.filename,
            "file_type": get_file_extension(file_path),
            "metadata": metadata,
            "parsed": parsed
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


@router.post("/{document_id}/analyze", response_model=StructureAnalysisResponse)
async def analyze_document_structure(document_id: str, current_user: dict = Depends(get_current_user)):
    """Run full structure analysis on a parsed document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        parsed = doc.get("parsed_json")
        if not parsed:
            raise HTTPException(status_code=400, detail="Document has not been parsed yet")

        filename = doc.get("filename") or ""
        file_ext = os.path.splitext(filename)[1].lstrip(".") if filename else "unknown"
        structured = struct_service.normalize_classification(parsed, file_type=file_ext)

        document_service.update_document(
            document_id,
            {"parsed_json": structured, "status": "structured", "updated_at": datetime.utcnow().isoformat() + "Z"},
        )

        return StructureAnalysisResponse(
            document_id=document_id,
            structured=structured,
            status="completed",
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/structure")
async def get_document_structure(document_id: str, current_user: dict = Depends(get_current_user)):
    """Get structured document data."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        parsed = doc.get("parsed_json")
        if not parsed:
            raise HTTPException(status_code=404, detail="Structure analysis not yet performed")

        backward_compatible = struct_service.get_backward_compatible(parsed)

        return {
            "document_id": document_id,
            "structured": parsed,
            "backward_compatible": backward_compatible,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/structure/validate")
async def validate_structure_endpoint(payload: dict, current_user: dict = Depends(get_current_user)):
    """Validate a structure JSON schema."""
    try:
        from app.services.structure.schema import StructuredDocument
        from app.services.structure.validator import validate_structure, generate_confidence_report

        structured = StructuredDocument(**payload)
        validation = validate_structure(structured)
        report = generate_confidence_report(structured)

        return {
            "validation": validation.model_dump(),
            "confidence_report": report.model_dump(),
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Validation failed: {str(e)}")


@router.get("/{document_id}/plagiarism")
async def get_plagiarism(document_id: str, current_user: dict = Depends(get_current_user)):
    """Get plagiarism reports for a document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        reports = plagiarism_service.get_plagiarism_reports_for_document(document_id)
        return {"document_id": document_id, "reports": reports}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}")
async def get_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Get a document by ID."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        return doc
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def list_documents(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
    offset: int = 0
):
    """List documents for the current user."""
    try:
        user_id = current_user.get("id")
        documents = document_service.list_documents_for_user(user_id, limit=limit, offset=offset)
        return {"documents": documents, "limit": limit, "offset": offset}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{document_id}")
async def delete_document(document_id: str, current_user: dict = Depends(get_current_user)):
    """Delete a document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")
        
        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized to delete this document")
        
        document_service.delete_document(document_id)
        return {"message": "Document deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{document_id}/jobs")
async def enqueue_job(document_id: str, payload: dict, current_user: dict = Depends(get_current_user)):
    """Create a job for a document. Payload should include 'type' (e.g., 'plagiarism', 'classify', 'structure', 'format')."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        job_type = payload.get("type")
        if not job_type:
            raise HTTPException(status_code=400, detail="Missing job type")
        
        allowed_types = {"parse", "classify", "structure", "format", "plagiarism", "citation"}
        if job_type not in allowed_types:
            raise HTTPException(status_code=400, detail=f"Invalid job type. Allowed: {', '.join(allowed_types)}")
        
        job_payload = {
            "document_id": document_id,
            "type": job_type,
            "status": "pending",
            "payload": payload.get("payload", {})
        }
        created = job_service.create_job(job_payload)
        return created
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/jobs")
async def get_document_jobs(document_id: str, current_user: dict = Depends(get_current_user)):
    """Get all jobs for a document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        jobs = job_service.list_jobs_for_document(document_id)
        return {"document_id": document_id, "jobs": jobs}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/format")
async def format_document(file: UploadFile = File(...), template: str = Form(...), current_user: dict = Depends(get_current_user)):
    """Format a document to a specific template. Currently supports IEEE."""
    if template != "ieee":
        raise HTTPException(status_code=400, detail="Only the 'ieee' template is currently supported.")
        
    file_path = await save_upload_file(file)
    try:
        parsed_data = parse_document(file_path)
        output_path = file_path.replace(os.path.splitext(file_path)[1], "_formatted.docx")
        generate_ieee_docx(parsed_data, output_path)
        
        return FileResponse(
            path=output_path, 
            filename=f"formatted_{file.filename}",
            media_type=MIME_TYPE_MAP.get(".docx", "application/octet-stream")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)
