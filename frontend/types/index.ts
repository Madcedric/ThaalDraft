export interface User {
  id: string;
  email: string;
  name?: string;
  provider: string;
  created_at?: string;
}

export interface Document {
  id: string;
  user_id?: string;
  filename: string;
  storage_path: string;
  status: DocumentStatus;
  parsed_json?: Record<string, unknown>;
  ai_classification?: Record<string, unknown>;
  structured_json?: StructuredData;
  citation_report?: CitationReport;
  compliance_report?: ComplianceReport;
  review_report?: ReviewReport;
  size_bytes?: number;
  file_type?: string;
  created_at: string;
  updated_at?: string;
  selected_journal?: string;
}

export type DocumentStatus = "uploaded" | "parsing" | "parsed" | "classifying" | "classified" | "structuring" | "structured" | "formatting" | "formatted" | "failed";

export interface StructuredData {
  title?: string;
  authors?: Array<{ name: string; affiliation?: string; email?: string }>;
  abstract?: string;
  keywords?: string[];
  sections?: Array<{
    heading: string;
    label: string;
    content: string;
    confidence: number;
    level?: number;
  }>;
  references?: Array<{
    raw_text: string;
    doi?: string;
    authors?: string[];
    title?: string;
    year?: number;
    journal?: string;
  }>;
  citations?: string[];
  metadata?: {
    word_count?: number;
    section_count?: number;
    reference_count?: number;
    has_abstract?: boolean;
    has_references?: boolean;
    doi?: string;
  };
  processing_metadata?: {
    file_type?: string;
    parser_used?: string;
    classification_method?: string;
    processing_time_ms?: number;
  };
  confidence_report?: {
    overall_confidence?: number;
    detected_labels?: string[];
    missing_labels?: string[];
    warnings?: string[];
  };
}

export interface Citation {
  id: string;
  raw_text: string;
  type: "numeric" | "author_year" | "unknown";
  source_section: string;
  reference_index: number;
  is_resolved: boolean;
  confidence: number;
}

export interface ReferenceValidation {
  raw_text: string;
  cited_count: number;
  is_cited: boolean;
  doi?: string;
  is_valid_doi: boolean;
  year?: number;
  authors: string[];
  title?: string;
  journal?: string;
}

export interface CitationIssue {
  type: "missing_reference" | "unused_reference" | "broken_citation" | "duplicate_reference" | "low_confidence" | "doi_not_found";
  severity: "error" | "warning" | "info";
  message: string;
  citation_id?: string;
  reference_index?: number;
}

export interface CitationHealthScore {
  overall: number;
  reference_coverage: number;
  citation_validity: number;
  duplicate_score: number;
  broken_score: number;
  doi_score: number;
  explanation: string;
}

export interface CitationReport {
  document_id: string;
  citation_style: string;
  total_citations: number;
  total_references: number;
  resolved_citations: number;
  unresolved_citations: number;
  citations: Citation[];
  references: ReferenceValidation[];
  issues: CitationIssue[];
  health_score: CitationHealthScore;
  processing_metadata?: {
    processing_time_ms: number;
    external_api_calls: number;
  };
  created_at: string;
}

export interface ComplianceIssue {
  check_type: "word_count" | "abstract_length" | "reference_count" | "citation_style" | "figure_limit" | "section_structure" | "keyword_count" | "author_count" | "title_length" | "doi_required";
  status: "pass" | "fail" | "warn";
  severity: "error" | "warning" | "info";
  message: string;
  actual_value?: string;
  expected_value?: string;
  recommendation?: string;
}

export interface ComplianceScore {
  overall: number;
  word_count: number;
  abstract_length: number;
  reference_count: number;
  citation_style: number;
  figure_limit: number;
  section_structure: number;
  explanation: string;
}

export interface ComplianceReport {
  document_id: string;
  journal_id: string;
  journal_name: string;
  score: ComplianceScore;
  issues: ComplianceIssue[];
  checks_performed: number;
  checks_passed: number;
  checks_failed: number;
  checks_warned: number;
  processing_metadata?: {
    processing_time_ms: number;
    journal_rule_applied: string;
  };
  created_at: string;
}

export interface JournalRule {
  journal_id: string;
  journal_name: string;
  min_words?: number;
  max_words?: number;
  min_abstract_words?: number;
  max_abstract_words?: number;
  min_references?: number;
  max_references?: number;
  citation_style: string;
  max_figures?: number;
  required_sections: string[];
  min_keywords?: number;
  max_keywords?: number;
  requires_doi: boolean;
  title_max_words?: number;
  description: string;
}

export interface ReviewStrength {
  category: "writing_quality" | "research_clarity" | "methodology" | "literature_coverage" | "citation_completeness" | "research_gaps";
  title: string;
  description: string;
}

export interface ReviewFinding {
  category: "writing_quality" | "research_clarity" | "methodology" | "literature_coverage" | "citation_completeness" | "research_gaps";
  severity: "critical" | "major" | "minor" | "suggestion";
  title: string;
  description: string;
  recommendation?: string;
  section_ref?: string;
}

export interface CategoryScore {
  category: "writing_quality" | "research_clarity" | "methodology" | "literature_coverage" | "citation_completeness" | "research_gaps";
  score: number;
  summary: string;
  finding_count: number;
}

export interface PublicationReadiness {
  overall: number;
  label: string;
  summary: string;
}

export interface ReviewReport {
  document_id: string;
  journal_id?: string;
  strengths: ReviewStrength[];
  weaknesses: ReviewFinding[];
  missing_references: string[];
  improvement_suggestions: string[];
  category_scores: CategoryScore[];
  publication_readiness: PublicationReadiness;
  total_findings: number;
  critical_count: number;
  major_count: number;
  minor_count: number;
  suggestion_count: number;
  analysis_method: string;
  processing_metadata?: {
    processing_time_ms: number;
    sections_analyzed: number;
    references_count: number;
  };
  created_at: string;
}

export interface Journal {
  id: string;
  name: string;
  shortName: string;
  citationStyle: string;
  description: string;
  url?: string;
}

export interface Job {
  id: string;
  document_id: string;
  type: JobType;
  status: JobStatus;
  payload?: Record<string, unknown>;
  result?: unknown;
  created_at: string;
  started_at?: string;
  finished_at?: string;
}

export type JobType = "parse" | "classify" | "structure" | "format" | "plagiarism" | "citation" | "compliance";

export type JobStatus = "pending" | "started" | "completed" | "failed";

export interface PlagiarismCheck {
  id: string;
  document_id: string;
  report?: Record<string, unknown>;
  similarity_score?: number;
  created_at: string;
}

export interface Export {
  id: string;
  document_id: string;
  format: ExportFormat;
  storage_path: string;
  created_at: string;
}

export type ExportFormat = "docx" | "pdf";

export type TemplateId = "ieee" | "apa" | "mla" | "acm" | "springer" | "elsevier" | "nature" | "custom";

export interface Template {
  id: TemplateId;
  name: string;
  description: string;
}

export interface ApiResponse<T> {
  data?: T;
  error?: string;
  detail?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  limit: number;
}

export interface UploadProgress {
  step: number;
  label: string;
  active: boolean;
  success?: boolean;
}
