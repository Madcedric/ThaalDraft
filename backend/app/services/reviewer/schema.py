from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ReviewCategory(str, Enum):
    WRITING_QUALITY = "writing_quality"
    RESEARCH_CLARITY = "research_clarity"
    METHODOLOGY = "methodology"
    LITERATURE_COVERAGE = "literature_coverage"
    CITATION_COMPLETENESS = "citation_completeness"
    RESEARCH_GAPS = "research_gaps"


class ReviewSeverity(str, Enum):
    CRITICAL = "critical"
    MAJOR = "major"
    MINOR = "minor"
    SUGGESTION = "suggestion"


class ReviewFinding(BaseModel):
    category: ReviewCategory
    severity: ReviewSeverity
    title: str
    description: str
    recommendation: str = ""
    section_ref: Optional[str] = None


class ReviewStrength(BaseModel):
    category: ReviewCategory
    title: str
    description: str


class CategoryScore(BaseModel):
    category: ReviewCategory
    score: float = Field(ge=0.0, le=100.0)
    summary: str = ""
    finding_count: int = 0


class PublicationReadiness(BaseModel):
    overall: float = Field(ge=0.0, le=100.0)
    label: str = ""
    summary: str = ""


class ReviewReport(BaseModel):
    document_id: str
    journal_id: Optional[str] = None
    strengths: List[ReviewStrength] = []
    weaknesses: List[ReviewFinding] = []
    missing_references: List[str] = []
    improvement_suggestions: List[str] = []
    category_scores: List[CategoryScore] = []
    publication_readiness: PublicationReadiness = PublicationReadiness()
    total_findings: int = 0
    critical_count: int = 0
    major_count: int = 0
    minor_count: int = 0
    suggestion_count: int = 0
    analysis_method: str = "deterministic"
    processing_metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class ReviewAnalysisRequest(BaseModel):
    journal_id: Optional[str] = None
    force_reanalysis: bool = False


class ReviewAnalysisResponse(BaseModel):
    document_id: str
    report: ReviewReport
    status: str = "completed"
