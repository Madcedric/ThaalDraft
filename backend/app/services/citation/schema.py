from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CitationType(str, Enum):
    NUMERIC = "numeric"
    AUTHOR_YEAR = "author_year"
    UNKNOWN = "unknown"


class CitationStyle(str, Enum):
    IEEE = "ieee"
    APA = "apa"
    HARVARD = "harvard"
    VANCOUVER = "vancouver"
    MLA = "mla"
    ACS = "acs"
    UNKNOWN = "unknown"


class CitationIssueType(str, Enum):
    MISSING_REFERENCE = "missing_reference"
    UNUSED_REFERENCE = "unused_reference"
    BROKEN_CITATION = "broken_citation"
    DUPLICATE_REFERENCE = "duplicate_reference"
    LOW_CONFIDENCE = "low_confidence"
    DOI_NOT_FOUND = "doi_not_found"


class CitationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class Citation(BaseModel):
    id: str
    raw_text: str
    type: CitationType = CitationType.UNKNOWN
    source_section: str = ""
    reference_index: int = -1
    is_resolved: bool = False
    confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    position_start: Optional[int] = None
    position_end: Optional[int] = None


class ReferenceValidation(BaseModel):
    raw_text: str
    cited_count: int = 0
    is_cited: bool = False
    doi: Optional[str] = None
    is_valid_doi: bool = False
    year: Optional[int] = None
    authors: List[str] = []
    title: Optional[str] = None
    journal: Optional[str] = None


class CitationIssue(BaseModel):
    type: CitationIssueType
    severity: CitationSeverity
    message: str
    citation_id: Optional[str] = None
    reference_index: Optional[int] = None


class CitationHealthScore(BaseModel):
    overall: float = Field(ge=0.0, le=100.0, default=0.0)
    reference_coverage: float = Field(ge=0.0, le=100.0, default=0.0)
    citation_validity: float = Field(ge=0.0, le=100.0, default=0.0)
    duplicate_score: float = Field(ge=0.0, le=100.0, default=0.0)
    broken_score: float = Field(ge=0.0, le=100.0, default=0.0)
    doi_score: float = Field(ge=0.0, le=100.0, default=0.0)
    explanation: str = ""


class CitationReport(BaseModel):
    document_id: str
    citation_style: CitationStyle = CitationStyle.UNKNOWN
    total_citations: int = 0
    total_references: int = 0
    resolved_citations: int = 0
    unresolved_citations: int = 0
    citations: List[Citation] = []
    references: List[ReferenceValidation] = []
    issues: List[CitationIssue] = []
    health_score: CitationHealthScore = CitationHealthScore()
    processing_metadata: Optional[dict] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class CitationAnalysisRequest(BaseModel):
    force_reanalysis: bool = False


class CitationAnalysisResponse(BaseModel):
    document_id: str
    report: CitationReport
    status: str = "completed"
