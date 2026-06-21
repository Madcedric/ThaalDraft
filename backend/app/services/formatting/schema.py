from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class FormatType(str, Enum):
    IEEE = "ieee"
    APA = "apa"
    MLA = "mla"
    ACM = "acm"
    SPRINGER = "springer"
    ELSEVIER = "elsevier"


class ExportType(str, Enum):
    DOCX = "docx"
    PDF = "pdf"
    LATEX = "latex"


class FontConfig(BaseModel):
    name: str = "Times New Roman"
    size_pt: int = 10
    bold: bool = False
    italic: bool = False


class MarginConfig(BaseModel):
    top_inches: float = 1.0
    bottom_inches: float = 1.0
    left_inches: float = 1.0
    right_inches: float = 1.0


class HeadingConfig(BaseModel):
    level: int
    font_name: str = "Times New Roman"
    font_size_pt: int = 12
    bold: bool = True
    italic: bool = False
    small_caps: bool = False
    alignment: str = "left"
    space_before_pt: float = 12
    space_after_pt: float = 6


class CitationStyleConfig(BaseModel):
    style: str
    in_text_format: str = ""
    reference_format: str = ""
    numbering: bool = False


class FormatTemplate(BaseModel):
    id: str
    name: str
    description: str
    body_font: FontConfig = FontConfig()
    title_font: FontConfig = FontConfig(size_pt=24, bold=True)
    abstract_font: FontConfig = FontConfig(italic=True)
    margins: MarginConfig = MarginConfig()
    headings: List[HeadingConfig] = []
    citation_style: CitationStyleConfig = CitationStyleConfig(style="unknown")
    column_count: int = 1
    line_spacing: float = 1.0
    abstract_label: str = "Abstract"
    references_label: str = "References"
    figure_caption_prefix: str = "Fig."
    table_caption_prefix: str = "TABLE"
    requires_keywords: bool = False
    keywords_label: str = "Keywords"
    page_numbering: bool = True
    two_column: bool = False


class FormatValidation(BaseModel):
    is_valid: bool
    issues: List[str] = []
    warnings: List[str] = []
    score: float = Field(ge=0.0, le=100.0, default=0.0)


class FormattedOutput(BaseModel):
    document_id: str
    template_id: str
    export_type: ExportType
    file_path: Optional[str] = None
    storage_path: Optional[str] = None
    validation: FormatValidation = FormatValidation(is_valid=True)
    processing_metadata: Optional[Dict[str, Any]] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat() + "Z")


class FormatRequest(BaseModel):
    template_id: str
    export_type: ExportType = ExportType.DOCX
    validate_only: bool = False


class FormatResponse(BaseModel):
    document_id: str
    output: FormattedOutput
    status: str = "completed"
