import { Document, Job, PlagiarismCheck, Export, CitationReport, ComplianceReport, ReviewReport, JournalRule, FormatTemplate, FormattedOutput, SubmissionPackage } from "@/types";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function apiFetch<T>(path: string, options: RequestInit = {}): Promise<T> {
  const url = `${API_BASE}${path}`;
  const response = await fetch(url, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `API error: ${response.status}`);
  }

  return response.json();
}

async function authFetch<T>(path: string, token: string, options: RequestInit = {}): Promise<T> {
  return apiFetch<T>(path, {
    ...options,
    headers: {
      Authorization: `Bearer ${token}`,
      ...options.headers,
    },
  });
}

// ── Upload ──────────────────────────────────────────────────────────────────

export interface UploadDocumentResponse {
  id: string;
  filename: string;
  storage_path: string;
  status: string;
  size_bytes?: number;
}

export async function uploadDocument(
  file: File,
  token: string,
  mode: string = "reconstruction"
): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("mode", mode);

  const url = `${API_BASE}/api/v1/documents/upload`;
  const response = await fetch(url, {
    method: "POST",
    headers: { Authorization: `Bearer ${token}` },
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || "Failed to upload document");
  }

  return response.json();
}

// ── Documents ───────────────────────────────────────────────────────────────

export async function getDocument(documentId: string, token: string): Promise<Document> {
  return authFetch<Document>(`/api/v1/documents/${documentId}`, token);
}

export async function listDocuments(token: string, limit = 50): Promise<{ documents: Document[] }> {
  return authFetch(`/api/v1/documents/?limit=${limit}`, token);
}

export async function updateDocument(
  documentId: string,
  updates: Record<string, unknown>,
  token: string
): Promise<Document> {
  return authFetch<Document>(`/api/v1/documents/${documentId}`, token, {
    method: "PATCH",
    body: JSON.stringify(updates),
  });
}

export async function deleteDocument(documentId: string, token: string): Promise<void> {
  await authFetch(`/api/v1/documents/${documentId}`, token, { method: "DELETE" });
}

// ── Jobs ────────────────────────────────────────────────────────────────────

export async function getDocumentJobs(documentId: string, token: string): Promise<{ document_id: string; jobs: Job[] }> {
  return authFetch(`/api/v1/documents/${documentId}/jobs`, token);
}

export async function enqueueJob(
  documentId: string,
  jobType: string,
  token: string,
  payload?: Record<string, unknown>
): Promise<Job> {
  return authFetch<Job>(`/api/v1/documents/${documentId}/jobs`, token, {
    method: "POST",
    body: JSON.stringify({ type: jobType, payload }),
  });
}

// ── Structure Analysis ──────────────────────────────────────────────────────

export async function runStructureAnalysis(
  documentId: string,
  token: string
): Promise<{ document_id: string; structured: Record<string, unknown>; status: string }> {
  return authFetch(`/api/v1/documents/${documentId}/analyze`, token, { method: "POST" });
}

// ── Citations ───────────────────────────────────────────────────────────────

export async function analyzeCitations(
  documentId: string,
  token: string
): Promise<{ document_id: string; report: CitationReport; status: string }> {
  return authFetch(`/api/v1/documents/${documentId}/citations/analyze`, token, { method: "POST" });
}

export async function getCitationReport(
  documentId: string,
  token: string
): Promise<{ document_id: string; report: CitationReport }> {
  return authFetch(`/api/v1/documents/${documentId}/citations`, token);
}

export async function getCitationHealth(
  documentId: string,
  token: string
): Promise<{ document_id: string; health_score: Record<string, number>; total_citations: number; total_references: number; resolved_citations: number }> {
  return authFetch(`/api/v1/documents/${documentId}/citations/health`, token);
}

// ── Compliance ──────────────────────────────────────────────────────────────

export async function getJournalRules(token: string): Promise<{ journals: JournalRule[] }> {
  return authFetch("/api/v1/documents/compliance/journals", token);
}

export async function getJournalRule(
  journalId: string,
  token: string
): Promise<JournalRule> {
  return authFetch(`/api/v1/documents/compliance/journals/${journalId}`, token);
}

export async function analyzeCompliance(
  documentId: string,
  journalId: string,
  token: string,
  forceReanalysis = false
): Promise<{ document_id: string; report: ComplianceReport; status: string }> {
  return authFetch(`/api/v1/documents/${documentId}/compliance/analyze`, token, {
    method: "POST",
    body: JSON.stringify({ journal_id: journalId, force_reanalysis: forceReanalysis }),
  });
}

export async function getComplianceReport(
  documentId: string,
  token: string
): Promise<{ document_id: string; report: ComplianceReport }> {
  return authFetch(`/api/v1/documents/${documentId}/compliance`, token);
}

// ── Reviewer ────────────────────────────────────────────────────────────────

export async function analyzeReview(
  documentId: string,
  token: string,
  journalId?: string
): Promise<{ document_id: string; report: ReviewReport; status: string }> {
  return authFetch(`/api/v1/documents/${documentId}/review/analyze`, token, {
    method: "POST",
    body: JSON.stringify({ journal_id: journalId || null, force_reanalysis: false }),
  });
}

export async function getReviewReport(
  documentId: string,
  token: string
): Promise<{ document_id: string; report: ReviewReport }> {
  return authFetch(`/api/v1/documents/${documentId}/review`, token);
}

// ── Formatting ──────────────────────────────────────────────────────────────

export async function getFormatTemplates(token: string): Promise<{ templates: FormatTemplate[] }> {
  return authFetch("/api/v1/formatting/templates", token);
}

export async function getFormatTemplate(
  templateId: string,
  token: string
): Promise<FormatTemplate> {
  return authFetch(`/api/v1/formatting/templates/${templateId}`, token);
}

export async function previewFormatting(
  documentId: string,
  templateId: string,
  token: string
): Promise<{ document_id: string; template_id: string; validation: { is_valid: boolean; issues: string[]; warnings: string[]; score: number } }> {
  return authFetch(`/api/v1/documents/${documentId}/formatting/preview`, token, {
    method: "POST",
    body: JSON.stringify({ template_id: templateId, validate_only: true }),
  });
}

export async function formatDocument(
  documentId: string,
  templateId: string,
  token: string,
  exportType: "docx" | "pdf" = "docx"
): Promise<{ document_id: string; output: FormattedOutput; status: string }> {
  return authFetch(`/api/v1/documents/${documentId}/formatting/format`, token, {
    method: "POST",
    body: JSON.stringify({ template_id: templateId, export_type: exportType }),
  });
}

export async function getFormattingStatus(
  documentId: string,
  token: string
): Promise<{ document_id: string; status: string; message: string }> {
  return authFetch(`/api/v1/documents/${documentId}/formatting`, token);
}

// ── Export / Plagiarism ─────────────────────────────────────────────────────

export async function analyzePlagiarism(
  documentId: string,
  token: string
): Promise<{ document_id: string; report: Record<string, unknown>; status: string }> {
  return authFetch(`/api/v1/documents/${documentId}/plagiarism/analyze`, token, { method: "POST" });
}

export async function requestExport(
  documentId: string,
  template: string,
  format: string,
  token: string
): Promise<{ job: Job }> {
  return authFetch(`/api/v1/documents/${documentId}/export`, token, {
    method: "POST",
    body: JSON.stringify({ template, format }),
  });
}

export async function getExports(
  documentId: string,
  token: string
): Promise<{ exports: Export[] }> {
  return authFetch(`/api/v1/documents/${documentId}/exports`, token);
}

export async function downloadExport(
  exportId: string,
  token: string
): Promise<{ download_url: string }> {
  return authFetch(`/api/v1/documents/download/${exportId}`, token);
}

export async function getPlagiarismReports(
  documentId: string,
  token: string
): Promise<{ document_id: string; reports: PlagiarismCheck[] }> {
  return authFetch(`/api/v1/documents/${documentId}/plagiarism`, token);
}

// ── Submission Package ──────────────────────────────────────────────────────

export async function buildSubmissionPackage(
  documentId: string,
  journalId: string,
  token: string,
  components?: string[]
): Promise<{ package: SubmissionPackage; total_components: number; completed_components: number; failed_components: number; overall_progress: number }> {
  return authFetch(`/api/v1/documents/${documentId}/submission/build`, token, {
    method: "POST",
    body: JSON.stringify({
      journal_id: journalId,
      components: components || [
        "manuscript_docx",
        "compliance_report",
        "review_report",
        "citation_report",
        "cover_letter",
        "author_statement",
        "conflict_statement",
      ],
    }),
  });
}

export async function getSubmissionPackage(
  documentId: string,
  token: string
): Promise<{ package: SubmissionPackage; total_components: number; completed_components: number }> {
  return authFetch(`/api/v1/documents/${documentId}/submission`, token);
}

export async function downloadSubmissionZip(
  documentId: string,
  token: string
): Promise<Blob> {
  const url = `${API_BASE}/api/v1/documents/${documentId}/submission/download-zip`;
  const response = await fetch(url, {
    method: "GET",
    headers: { Authorization: `Bearer ${token}` },
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `ZIP download failed: ${response.status}`);
  }
  return response.blob();
}

// ── Export (file download) ──────────────────────────────────────────────────

export interface ExportResult {
  blob: Blob;
  filename: string;
  contentType: string;
}

export async function exportDocument(
  documentId: string,
  template: string,
  format: string,
  token: string
): Promise<ExportResult> {
  const url = `${API_BASE}/api/v1/documents/${documentId}/export`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`,
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ template, format }),
  });
  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || `Export failed: ${response.status}`);
  }
  const blob = await response.blob();
  const disposition = response.headers.get("Content-Disposition") || "";
  const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
  const filename = filenameMatch
    ? filenameMatch[1]
    : `${documentId}_${template}.${format}`;
  const contentType = response.headers.get("Content-Type") || "application/octet-stream";
  return { blob, filename, contentType };
}
