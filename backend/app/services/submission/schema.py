from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class PackageStatus(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


class PackageComponent(str, Enum):
    MANUSCRIPT_DOCX = "manuscript_docx"
    MANUSCRIPT_PDF = "manuscript_pdf"
    MANUSCRIPT_LATEX = "manuscript_latex"
    COMPLIANCE_REPORT = "compliance_report"
    REVIEW_REPORT = "review_report"
    COVER_LETTER = "cover_letter"
    AUTHOR_STATEMENT = "author_statement"
    CONFLICT_STATEMENT = "conflict_statement"
    CITATION_REPORT = "citation_report"


class PackageComponentItem(BaseModel):
    component: PackageComponent
    filename: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    status: str = "pending"
    error: Optional[str] = None


class CoverLetter(BaseModel):
    journal_name: str = ""
    editor_name: str = ""
    manuscript_title: str = ""
    authors: List[str] = []
    key_findings: str = ""
    significance: str = ""
    content: str = ""


class AuthorStatement(BaseModel):
    manuscript_title: str = ""
    authors: List[str] = []
    contributions: Dict[str, str] = {}
    content: str = ""


class ConflictStatement(BaseModel):
    manuscript_title: str = ""
    authors: List[str] = []
    conflicts: List[str] = []
    content: str = ""


class SubmissionPackage(BaseModel):
    document_id: str
    journal_id: str
    journal_name: str = ""
    template_id: str = ""
    status: PackageStatus = PackageStatus.PENDING
    components: List[PackageComponentItem] = []
    cover_letter: Optional[CoverLetter] = None
    author_statement: Optional[AuthorStatement] = None
    conflict_statement: Optional[ConflictStatement] = None
    zip_path: Optional[str] = None
    zip_size: Optional[int] = None
    processing_metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    completed_at: Optional[str] = None


class PackageBuildRequest(BaseModel):
    journal_id: str
    template_id: Optional[str] = None
    components: List[PackageComponent] = [
        PackageComponent.MANUSCRIPT_DOCX,
        PackageComponent.COMPLIANCE_REPORT,
        PackageComponent.REVIEW_REPORT,
        PackageComponent.COVER_LETTER,
    ]
    cover_letter: Optional[CoverLetter] = None
    author_statement: Optional[AuthorStatement] = None
    conflict_statement: Optional[ConflictStatement] = None


class PackageStatusResponse(BaseModel):
    package: SubmissionPackage
    total_components: int = 0
    completed_components: int = 0
    failed_components: int = 0
    overall_progress: float = Field(ge=0.0, le=100.0, default=0.0)


class PackageListResponse(BaseModel):
    packages: List[SubmissionPackage]
    total: int = 0
