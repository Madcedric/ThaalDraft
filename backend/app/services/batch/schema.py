from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class BatchJobStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BatchJobType(str, Enum):
    PARSE = "parse"
    CLASSIFY = "classify"
    STRUCTURE = "structure"
    FORMAT = "format"
    CITATION = "citation"
    COMPLIANCE = "compliance"
    REVIEW = "review"


class BatchFileStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class BatchFile(BaseModel):
    filename: str
    status: BatchFileStatus = BatchFileStatus.PENDING
    progress: float = Field(ge=0.0, le=100.0, default=0.0)
    error: Optional[str] = None
    document_id: Optional[str] = None
    file_size: Optional[int] = None


class BatchJob(BaseModel):
    id: str
    user_id: str
    job_type: BatchJobType
    status: BatchJobStatus = BatchJobStatus.PENDING
    total_files: int = 0
    completed_files: int = 0
    failed_files: int = 0
    files: List[BatchFile] = []
    payload: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    started_at: Optional[str] = None
    finished_at: Optional[str] = None


class BatchJobSummary(BaseModel):
    total_files: int = 0
    completed_files: int = 0
    failed_files: int = 0
    running_files: int = 0
    pending_files: int = 0
    overall_progress: float = Field(ge=0.0, le=100.0, default=0.0)


class BatchCreateRequest(BaseModel):
    job_type: BatchJobType
    template_id: Optional[str] = None
    payload: Optional[Dict[str, Any]] = None


class BatchUploadRequest(BaseModel):
    job_type: BatchJobType = BatchJobType.PARSE
    template_id: Optional[str] = None


class BatchStatusResponse(BaseModel):
    job: BatchJob
    summary: BatchJobSummary


class BatchJobListResponse(BaseModel):
    jobs: List[BatchJob]
    total: int = 0
