from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ComplianceCheckType(str, Enum):
    WORD_COUNT = "word_count"
    ABSTRACT_LENGTH = "abstract_length"
    REFERENCE_COUNT = "reference_count"
    CITATION_STYLE = "citation_style"
    FIGURE_LIMIT = "figure_limit"
    SECTION_STRUCTURE = "section_structure"
    KEYWORD_COUNT = "keyword_count"
    AUTHOR_COUNT = "author_count"
    TITLE_LENGTH = "title_length"
    DOI_REQUIRED = "doi_required"


class ComplianceSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ComplianceStatus(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    WARN = "warn"


class ComplianceIssue(BaseModel):
    check_type: ComplianceCheckType
    status: ComplianceStatus
    severity: ComplianceSeverity
    message: str
    actual_value: Optional[str] = None
    expected_value: Optional[str] = None
    recommendation: str = ""


class ComplianceScore(BaseModel):
    overall: float = Field(ge=0.0, le=100.0, default=0.0)
    word_count: float = Field(ge=0.0, le=100.0, default=0.0)
    abstract_length: float = Field(ge=0.0, le=100.0, default=0.0)
    reference_count: float = Field(ge=0.0, le=100.0, default=0.0)
    citation_style: float = Field(ge=0.0, le=100.0, default=0.0)
    figure_limit: float = Field(ge=0.0, le=100.0, default=0.0)
    section_structure: float = Field(ge=0.0, le=100.0, default=0.0)
    explanation: str = ""


class JournalRule(BaseModel):
    journal_id: str
    journal_name: str
    min_words: Optional[int] = None
    max_words: Optional[int] = None
    min_abstract_words: Optional[int] = None
    max_abstract_words: Optional[int] = None
    min_references: Optional[int] = None
    max_references: Optional[int] = None
    citation_style: str = "unknown"
    max_figures: Optional[int] = None
    required_sections: List[str] = []
    min_keywords: Optional[int] = None
    max_keywords: Optional[int] = None
    min_authors: Optional[int] = None
    max_authors: Optional[int] = None
    requires_doi: bool = False
    title_max_words: Optional[int] = None
    description: str = ""


class ComplianceReport(BaseModel):
    document_id: str
    journal_id: str
    journal_name: str
    score: ComplianceScore
    issues: List[ComplianceIssue] = []
    checks_performed: int = 0
    checks_passed: int = 0
    checks_failed: int = 0
    checks_warned: int = 0
    processing_metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class ComplianceAnalysisRequest(BaseModel):
    journal_id: str
    force_reanalysis: bool = False


class ComplianceAnalysisResponse(BaseModel):
    document_id: str
    report: ComplianceReport
    status: str = "completed"
