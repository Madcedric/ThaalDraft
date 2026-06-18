from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List
from app.services.batch import (
    BatchCreateRequest,
    BatchJob,
    BatchJobType,
    BatchStatusResponse,
    BatchJobListResponse,
    batch_manager,
)
from app.api.routes.auth import get_current_user

router = APIRouter()


@router.post("/batch/create", response_model=BatchJob)
async def create_batch_job(
    request: BatchCreateRequest,
    current_user: dict = Depends(get_current_user),
):
    """Create a new batch processing job."""
    try:
        user_id = current_user.get("id")
        job = batch_manager.create_job(user_id=user_id, request=request)
        return job
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/{job_id}/files")
async def add_files_to_batch(
    job_id: str,
    filenames: List[str],
    current_user: dict = Depends(get_current_user),
):
    """Add files to a batch job."""
    try:
        job = batch_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Batch job not found")

        if job.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        updated_job = batch_manager.add_files_to_job(job_id, filenames)
        if not updated_job:
            raise HTTPException(status_code=404, detail="Failed to add files")

        return {"job": updated_job.model_dump(), "files_added": len(filenames)}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/{job_id}/start")
async def start_batch_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Start processing a batch job."""
    try:
        job = batch_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Batch job not found")

        if job.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        if not job.files:
            raise HTTPException(status_code=400, detail="No files to process")

        updated_job = batch_manager.start_job(job_id)
        if not updated_job:
            raise HTTPException(status_code=500, detail="Failed to start job")

        return {"job": updated_job.model_dump(), "message": "Batch job started"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch/{job_id}/status", response_model=BatchStatusResponse)
async def get_batch_status(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get the status of a batch job."""
    try:
        job = batch_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Batch job not found")

        if job.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        summary = batch_manager.get_summary(job_id)
        return BatchStatusResponse(job=job, summary=summary)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/batch/{job_id}/cancel")
async def cancel_batch_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Cancel a batch job."""
    try:
        job = batch_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Batch job not found")

        if job.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        updated_job = batch_manager.cancel_job(job_id)
        if not updated_job:
            raise HTTPException(status_code=500, detail="Failed to cancel job")

        return {"job": updated_job.model_dump(), "message": "Batch job cancelled"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/batch/jobs", response_model=BatchJobListResponse)
async def list_batch_jobs(
    current_user: dict = Depends(get_current_user),
):
    """List all batch jobs for the current user."""
    try:
        user_id = current_user.get("id")
        jobs = batch_manager.get_user_jobs(user_id)
        return BatchJobListResponse(jobs=jobs, total=len(jobs))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/batch/{job_id}")
async def delete_batch_job(
    job_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete a batch job."""
    try:
        job = batch_manager.get_job(job_id)
        if not job:
            raise HTTPException(status_code=404, detail="Batch job not found")

        if job.user_id != current_user.get("id"):
            raise HTTPException(status_code=403, detail="Not authorized")

        deleted = batch_manager.delete_job(job_id)
        if not deleted:
            raise HTTPException(status_code=500, detail="Failed to delete job")

        return {"message": "Batch job deleted", "job_id": job_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
