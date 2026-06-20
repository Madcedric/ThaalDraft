from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import FileResponse
from typing import Dict, List, Optional
from app.services.submission import (
    PackageBuildRequest,
    PackageComponent,
    PackageStatusResponse,
    SubmissionPackage,
    build_submission_package,
)
from app.services import document_service
from app.api.routes.auth import get_current_user
import os
import zipfile

router = APIRouter()

_packages_store: Dict[str, SubmissionPackage] = {}


@router.post("/{document_id}/submission/build", response_model=PackageStatusResponse)
async def build_submission(
    document_id: str,
    request: PackageBuildRequest,
    current_user: dict = Depends(get_current_user),
):
    """Build a submission package for a document."""
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
                detail="Document must be structured before building submission package",
            )

        compliance_report = (doc.get("parsed_json") or {}).get("compliance_report")
        review_report = (doc.get("parsed_json") or {}).get("review_report")
        citation_report = (doc.get("parsed_json") or {}).get("citation_report")

        from app.services.compliance.rules import get_journal_rule
        journal_rule = get_journal_rule(request.journal_id)
        journal_name = journal_rule.journal_name if journal_rule else request.journal_id

        package = build_submission_package(
            document_id=document_id,
            journal_id=request.journal_id,
            journal_name=journal_name,
            template_id=request.template_id,
            components=request.components,
            structured_data=structured_data,
            compliance_report=compliance_report,
            review_report=review_report,
            citation_report=citation_report,
            cover_letter=request.cover_letter,
            author_statement=request.author_statement,
            conflict_statement=request.conflict_statement,
        )

        zip_path = _create_zip(package, document_id)
        if zip_path:
            package.zip_path = zip_path
            package.zip_size = os.path.getsize(zip_path) if os.path.exists(zip_path) else None

        _packages_store[document_id] = package

        total = len(package.components)
        completed = sum(1 for c in package.components if c.status == "completed")
        failed = sum(1 for c in package.components if c.status == "failed")
        progress = (completed / total * 100) if total > 0 else 0.0

        return PackageStatusResponse(
            package=package,
            total_components=total,
            completed_components=completed,
            failed_components=failed,
            overall_progress=round(progress, 1),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _create_zip(package: SubmissionPackage, document_id: str) -> Optional[str]:
    output_dir = "submission_packages"
    zip_path = os.path.join(output_dir, f"{document_id}_submission.zip")
    os.makedirs(output_dir, exist_ok=True)

    try:
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for comp in package.components:
                if comp.status == "completed" and comp.file_path and os.path.exists(comp.file_path):
                    arcname = comp.filename or os.path.basename(comp.file_path)
                    zf.write(comp.file_path, arcname)
        return zip_path
    except Exception as e:
        print(f"ZIP creation failed: {e}")
        return None


@router.get("/{document_id}/submission")
async def get_submission_package(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get existing submission package for a document."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        package = _packages_store.get(document_id)
        if not package:
            raise HTTPException(
                status_code=404,
                detail="No submission package found. Build one first.",
            )

        total = len(package.components)
        completed = sum(1 for c in package.components if c.status == "completed")
        failed = sum(1 for c in package.components if c.status == "failed")
        progress = (completed / total * 100) if total > 0 else 0.0

        return PackageStatusResponse(
            package=package,
            total_components=total,
            completed_components=completed,
            failed_components=failed,
            overall_progress=round(progress, 1),
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{document_id}/submission/download-zip")
async def download_submission_zip(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Download the submission package as a ZIP file."""
    try:
        doc = document_service.get_document(document_id)
        if not doc:
            raise HTTPException(status_code=404, detail="Document not found")

        if doc.get("user_id") != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        package = _packages_store.get(document_id)
        if not package:
            raise HTTPException(status_code=404, detail="No submission package found. Build one first.")

        if package.zip_path and os.path.exists(package.zip_path):
            return FileResponse(
                path=package.zip_path,
                filename=f"{document_id}_submission.zip",
                media_type="application/zip",
            )

        zip_path = _create_zip(package, document_id)
        if zip_path and os.path.exists(zip_path):
            package.zip_path = zip_path
            package.zip_size = os.path.getsize(zip_path)
            return FileResponse(
                path=zip_path,
                filename=f"{document_id}_submission.zip",
                media_type="application/zip",
            )

        raise HTTPException(status_code=500, detail="Failed to create ZIP package")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/submission/packages")
async def list_submission_packages(
    current_user: dict = Depends(get_current_user),
):
    """List all submission packages for the current user."""
    try:
        return {"packages": [p.model_dump() for p in _packages_store.values()], "total": len(_packages_store)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
