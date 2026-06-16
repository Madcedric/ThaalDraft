import { Document, Job, PlagiarismCheck, Export } from "@/types";

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

export interface UploadDocumentResponse {
  id: string;
  filename: string;
  storage_path: string;
  status: string;
  size_bytes?: number;
}

export async function uploadDocument(
  file: File,
  token: string
): Promise<UploadDocumentResponse> {
  const formData = new FormData();
  formData.append("file", file);

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

export async function getDocument(documentId: string, token: string): Promise<Document> {
  return authFetch<Document>(`/api/v1/documents/${documentId}`, token);
}

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

export async function getPlagiarismReports(
  documentId: string,
  token: string
): Promise<{ document_id: string; reports: PlagiarismCheck[] }> {
  return authFetch(`/api/v1/documents/${documentId}/plagiarism`, token);
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
