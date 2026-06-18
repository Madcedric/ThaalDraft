from typing import Dict, List, Optional
import uuid
import time
from .schema import (
    BatchFile,
    BatchFileStatus,
    BatchJob,
    BatchJobStatus,
    BatchJobType,
    BatchJobSummary,
    BatchCreateRequest,
)


class BatchManager:
    def __init__(self):
        self._jobs: Dict[str, BatchJob] = {}

    def create_job(
        self,
        user_id: str,
        request: BatchCreateRequest,
    ) -> BatchJob:
        job_id = str(uuid.uuid4())
        job = BatchJob(
            id=job_id,
            user_id=user_id,
            job_type=request.job_type,
            payload=request.payload,
            status=BatchJobStatus.PENDING,
        )
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
        return job

    def get_job(self, job_id: str) -> Optional[BatchJob]:
        return self._jobs.get(job_id)

    def get_user_jobs(self, user_id: str) -> List[BatchJob]:
        return [j for j in self._jobs.values() if j.user_id == user_id]

    def start_job(self, job_id: str) -> Optional[BatchJob]:
        job = self._jobs.get(job_id)
        if not job:
            return None
        job.status = BatchJobStatus.RUNNING
        job.started_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return job

    def update_file_status(
        self,
        job_id: str,
        filename: str,
        status: BatchFileStatus,
        document_id: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Optional[BatchJob]:
        job = self._jobs.get(job_id)
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

        return job

    def cancel_job(self, job_id: str) -> Optional[BatchJob]:
        job = self._jobs.get(job_id)
        if not job:
            return None
        job.status = BatchJobStatus.CANCELLED
        job.finished_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        return job

    def get_summary(self, job_id: str) -> Optional[BatchJobSummary]:
        job = self._jobs.get(job_id)
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
            return True
        return False


batch_manager = BatchManager()
