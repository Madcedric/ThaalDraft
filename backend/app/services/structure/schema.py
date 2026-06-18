from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Author(BaseModel):
    name: str
    affiliation: Optional[str] = None
    email: Optional[str] = None


class Section(BaseModel):
    heading: str
    label: str
    content: str
    confidence: float = Field(ge=0.0, le=1.0)
    level: int = 1
    start_position: Optional[int] = None
    end_position: Optional[int] = None


class Reference(BaseModel):
    raw_text: str
    doi: Optional[str] = None
    authors: Optional[List[str]] = None
    title: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    volume: Optional[str] = None
    pages: Optional[str] = None
    is_valid: bool = True


class ProcessingMetadata(BaseModel):
    file_type: str
    parser_used: str
    classification_method: str = "deterministic"
    processing_time_ms: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")
    version: str = "1.0"


class DocumentMetadata(BaseModel):
    doi: Optional[str] = None
    journal: Optional[str] = None
    date: Optional[str] = None
    keywords: List[str] = []
    word_count: int = 0
    section_count: int = 0
    reference_count: int = 0
    has_abstract: bool = False
    has_references: bool = False
    has_keywords: bool = False


class DetectedSection(BaseModel):
    heading: str
    label: str
    confidence: float = Field(ge=0.0, le=1.0)
    detection_method: str


class StructureConfidenceReport(BaseModel):
    overall_confidence: float = Field(ge=0.0, le=1.0, default=0.0)
    section_detections: List[DetectedSection] = []
    detected_labels: List[str] = []
    missing_labels: List[str] = []
    detection_methods_used: List[str] = []
    warnings: List[str] = []


class StructuredDocument(BaseModel):
    title: Optional[str] = None
    authors: List[Author] = []
    abstract: str = ""
    keywords: List[str] = []
    sections: List[Section] = []
    references: List[Reference] = []
    citations: List[str] = []
    tables: List[List[List[str]]] = []
    figures: List[str] = []
    metadata: DocumentMetadata = DocumentMetadata()
    processing_metadata: Optional[ProcessingMetadata] = None
    confidence_report: StructureConfidenceReport = StructureConfidenceReport()


class StructureAnalysisResponse(BaseModel):
    document_id: str
    structured: StructuredDocument
    status: str = "completed"


class StructureValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    completeness_score: float = Field(ge=0.0, le=1.0)
