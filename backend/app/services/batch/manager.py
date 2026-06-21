"""Batch Processing Manager — V2.

Supabase-backed batch processing with persistence.
Replaces in-memory BatchManager with database storage.
"""

import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests

from .schema import (
    BatchFile,
    BatchFileStatus,
    BatchJob,
    BatchJobStatus,
    BatchJobType,
    BatchJobSummary,
    BatchCreateRequest,
)

logger = logging.getLogger(__name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL", "")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")


def _headers() -> Dict[str, str]:
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation",
    }


class BatchManager:
    """Batch processing manager with Supabase persistence."""

    def __init__(self):
        self._jobs: Dict[str, BatchJob] = {}  # Local cache fallback

    def create_job(
        self,
        user_id: str,
        request: BatchCreateRequest,
    ) -> BatchJob:
        import uuid
        job_id = str(uuid.uuid4())
        job = BatchJob(
            id=job_id,
            user_id=user_id,
            job_type=request.job_type,
            payload=request.payload,
            status=BatchJobStatus.PENDING,
        )

        # Persist to Supabase
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                row = {
                    "id": job_id,
                    "user_id": user_id,
                    "job_type": request.job_type.value if hasattr(request.job_type, "value") else str(request.job_type),
                    "payload": request.payload or {},
                    "status": "pending",
                    "total_files": 0,
                    "completed_files": 0,
                    "failed_files": 0,
                }
                resp = requests.post(
                    f"{SUPABASE_URL}/rest/v1/batch_jobs",
                    headers=_headers(),
                    json=row,
                    timeout=10,
                )
                if resp.status_code not in (200, 201):
                    logger.warning(f"Failed to persist batch job: {resp.status_code}")
            except Exception as e:
                logger.warning(f"Batch job persistence failed: {e}")

        self._jobs[job_id] = job
        return job

    def add_files_to_job(
        self,
        job_id: str,
        filenames: List[str],
        file_sizes: Optional[List[int]] = None,
    ) -> Optional[BatchJob]:
        job = self._jobs.get(job_id)
        if not job:
            # Try loading from Supabase
            job = self._load_job(job_id)
            if not job:
                return None

        for i, filename in enumerate(filenames):
            file_size = file_sizes[i] if file_sizes and i < len(file_sizes) else None
            batch_file = BatchFile(
                filename=filename,
                status=BatchFileStatus.PENDING,
                file_size=file_size,
            )
            job.files.append(batch_file)

        job.total_files = len(job.files)

        # Update Supabase
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/batch_jobs?id=eq.{job_id}",
                    headers=_headers(),
                    json={"total_files": job.total_files},
                    timeout=10,
                )
                # Insert file records
                file_rows = []
                for f in job.files:
                    file_rows.append({
                        "batch_job_id": job_id,
                        "filename": f.filename,
                        "status": "pending",
                        "file_size": f.file_size,
                    })
                if file_rows:
                    requests.post(
                        f"{SUPABASE_URL}/rest/v1/batch_files",
                        headers=_headers(),
                        json=file_rows,
                        timeout=10,
                    )
            except Exception as e:
                logger.warning(f"Batch files persistence failed: {e}")

        return job

    def get_job(self, job_id: str) -> Optional[BatchJob]:
        if job_id in self._jobs:
            return self._jobs[job_id]
        return self._load_job(job_id)

    def get_user_jobs(self, user_id: str) -> List[BatchJob]:
        # Check local cache first
        local_jobs = [j for j in self._jobs.values() if j.user_id == user_id]
        if local_jobs:
            return local_jobs

        # Load from Supabase
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                resp = requests.get(
                    f"{SUPABASE_URL}/rest/v1/batch_jobs",
                    headers=_headers(),
                    params={
                        "user_id": f"eq.{user_id}",
                        "order": "created_at.desc",
                        "limit": 50,
                    },
                    timeout=10,
                )
                if resp.status_code == 200:
                    rows = resp.json()
                    jobs = []
                    for row in rows:
                        job = self._row_to_job(row)
                        self._jobs[job.id] = job
                        jobs.append(job)
                    return jobs
            except Exception as e:
                logger.warning(f"Failed to load user batch jobs: {e}")

        return []

    def start_job(self, job_id: str) -> Optional[BatchJob]:
        job = self.get_job(job_id)
        if not job:
            return None
        job.status = BatchJobStatus.RUNNING
        job.started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if SUPABASE_URL and SUPABASE_KEY:
            try:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/batch_jobs?id=eq.{job_id}",
                    headers=_headers(),
                    json={"status": "running", "started_at": job.started_at},
                    timeout=10,
                )
            except Exception as e:
                logger.warning(f"Failed to update batch job status: {e}")

        return job

    def update_file_status(
        self,
        job_id: str,
        filename: str,
        status: BatchFileStatus,
        document_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[BatchJob]:
        job = self.get_job(job_id)
        if not job:
            return None

        for f in job.files:
            if f.filename == filename:
                f.status = status
                f.document_id = document_id
                f.error = error
                if status == BatchFileStatus.COMPLETED:
                    job.completed_files += 1
                elif status == BatchFileStatus.FAILED:
                    job.failed_files += 1
                break

        all_done = all(
            f.status in (BatchFileStatus.COMPLETED, BatchFileStatus.FAILED)
            for f in job.files
        )
        if all_done and job.files:
            job.status = BatchJobStatus.COMPLETED
            job.finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        # Update Supabase
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/batch_jobs?id=eq.{job_id}",
                    headers=_headers(),
                    json={
                        "status": job.status.value if hasattr(job.status, "value") else str(job.status),
                        "completed_files": job.completed_files,
                        "failed_files": job.failed_files,
                        "finished_at": job.finished_at,
                    },
                    timeout=10,
                )
                # Update file record
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/batch_files",
                    headers=_headers(),
                    params={"batch_job_id": f"eq.{job_id}", "filename": f"eq.{filename}"},
                    json={
                        "status": status.value if hasattr(status, "value") else str(status),
                        "document_id": document_id,
                        "error": error,
                    },
                    timeout=10,
                )
            except Exception as e:
                logger.warning(f"Failed to update batch file status: {e}")

        return job

    def cancel_job(self, job_id: str) -> Optional[BatchJob]:
        job = self.get_job(job_id)
        if not job:
            return None
        job.status = BatchJobStatus.CANCELLED
        job.finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

        if SUPABASE_URL and SUPABASE_KEY:
            try:
                requests.patch(
                    f"{SUPABASE_URL}/rest/v1/batch_jobs?id=eq.{job_id}",
                    headers=_headers(),
                    json={"status": "cancelled", "finished_at": job.finished_at},
                    timeout=10,
                )
            except Exception as e:
                logger.warning(f"Failed to cancel batch job: {e}")

        return job

    def get_summary(self, job_id: str) -> Optional[BatchJobSummary]:
        job = self.get_job(job_id)
        if not job:
            return None

        running = sum(1 for f in job.files if f.status == BatchFileStatus.PROCESSING)
        pending = sum(1 for f in job.files if f.status == BatchFileStatus.PENDING)
        total = len(job.files)
        progress = (job.completed_files / total * 100) if total > 0 else 0.0

        return BatchJobSummary(
            total_files=total,
            completed_files=job.completed_files,
            failed_files=job.failed_files,
            running_files=running,
            pending_files=pending,
            overall_progress=round(progress, 1),
        )

    def delete_job(self, job_id: str) -> bool:
        if job_id in self._jobs:
            del self._jobs[job_id]

        if SUPABASE_URL and SUPABASE_KEY:
            try:
                # Delete files first
                requests.delete(
                    f"{SUPABASE_URL}/rest/v1/batch_files",
                    headers=_headers(),
                    params={"batch_job_id": f"eq.{job_id}"},
                    timeout=10,
                )
                # Delete job
                resp = requests.delete(
                    f"{SUPABASE_URL}/rest/v1/batch_jobs",
                    headers=_headers(),
                    params={"id": f"eq.{job_id}"},
                    timeout=10,
                )
                return resp.status_code in (200, 204)
            except Exception as e:
                logger.warning(f"Failed to delete batch job: {e}")

        return False

    def _load_job(self, job_id: str) -> Optional[BatchJob]:
        """Load a batch job from Supabase."""
        if not SUPABASE_URL or not SUPABASE_KEY:
            return None

        try:
            resp = requests.get(
                f"{SUPABASE_URL}/rest/v1/batch_jobs",
                headers=_headers(),
                params={"id": f"eq.{job_id}"},
                timeout=10,
            )
            if resp.status_code == 200:
                rows = resp.json()
                if rows:
                    job = self._row_to_job(rows[0])
                    self._jobs[job_id] = job
                    return job
        except Exception as e:
            logger.warning(f"Failed to load batch job: {e}")

        return None

    def _row_to_job(self, row: Dict[str, Any]) -> BatchJob:
        """Convert a Supabase row to a BatchJob."""
        status_str = row.get("status", "pending")
        try:
            status = BatchJobStatus(status_str)
        except ValueError:
            status = BatchJobStatus.PENDING

        job_type_str = row.get("job_type", "format")
        try:
            job_type = BatchJobType(job_type_str)
        except ValueError:
            job_type = BatchJobType.FORMAT

        job = BatchJob(
            id=row["id"],
            user_id=row.get("user_id", ""),
            job_type=job_type,
            payload=row.get("payload", {}),
            status=status,
            total_files=row.get("total_files", 0),
            completed_files=row.get("completed_files", 0),
            failed_files=row.get("failed_files", 0),
            started_at=row.get("started_at"),
            finished_at=row.get("finished_at"),
        )

        # Load files
        if SUPABASE_URL and SUPABASE_KEY:
            try:
                resp = requests.get(
                    f"{SUPABASE_URL}/rest/v1/batch_files",
                    headers=_headers(),
                    params={"batch_job_id": f"eq.{row['id']}", "order": "created_at.asc"},
                    timeout=10,
                )
                if resp.status_code == 200:
                    for f_row in resp.json():
                        f_status_str = f_row.get("status", "pending")
                        try:
                            f_status = BatchFileStatus(f_status_str)
                        except ValueError:
                            f_status = BatchFileStatus.PENDING

                        job.files.append(BatchFile(
                            filename=f_row["filename"],
                            status=f_status,
                            file_size=f_row.get("file_size"),
                            document_id=f_row.get("document_id"),
                            error=f_row.get("error"),
                        ))
            except Exception as e:
                logger.warning(f"Failed to load batch files: {e}")

        return job


batch_manager = BatchManager()
