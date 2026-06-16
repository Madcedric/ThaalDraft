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
  structured_json?: Record<string, unknown>;
  size_bytes?: number;
  created_at: string;
  updated_at?: string;
}

export type DocumentStatus = "uploaded" | "parsing" | "parsed" | "classifying" | "classified" | "structuring" | "structured" | "formatting" | "formatted" | "failed";

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

export type JobType = "parse" | "classify" | "structure" | "format" | "plagiarism";

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

export type TemplateId = "ieee" | "apa" | "mla" | "acm" | "springer" | "elsevier" | "nature";

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
