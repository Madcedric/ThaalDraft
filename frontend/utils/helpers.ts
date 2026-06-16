import { TemplateId, Template } from "@/types";

export const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export const TEMPLATES: Template[] = [
  { id: "ieee", name: "IEEE Standard", description: "Two-column technical format" },
  { id: "apa", name: "APA 7th Edition", description: "Standard psychological format" },
  { id: "mla", name: "MLA 9th Edition", description: "Humanities formatting" },
  { id: "acm", name: "ACM Proceedings", description: "Computer science conferences" },
  { id: "springer", name: "Springer LNCS", description: "Lecture notes format" },
  { id: "elsevier", name: "Elsevier Journal", description: "Scientific journal format" },
  { id: "nature", name: "Nature Journal", description: "Single-column scientific" },
];

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return "0 Bytes";
  const k = 1024;
  const sizes = ["Bytes", "KB", "MB", "GB"];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
}

export function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

export function getStatusColor(status: string): string {
  const statusColors: Record<string, string> = {
    uploaded: "text-muted-foreground",
    parsing: "text-blue-500",
    parsed: "text-blue-600",
    classifying: "text-purple-500",
    classified: "text-purple-600",
    structuring: "text-indigo-500",
    structured: "text-indigo-600",
    formatting: "text-green-500",
    formatted: "text-green-600",
    failed: "text-destructive",
    pending: "text-muted-foreground",
    started: "text-blue-500",
    completed: "text-green-600",
  };
  return statusColors[status] || "text-muted-foreground";
}

export function getJobTypeLabel(type: string): string {
  const labels: Record<string, string> = {
    parse: "Document Parsing",
    classify: "AI Classification",
    structure: "Structure Analysis",
    format: "Format Generation",
    plagiarism: "Plagiarism Check",
  };
  return labels[type] || type;
}

export function getTemplateById(id: TemplateId): Template | undefined {
  return TEMPLATES.find((t) => t.id === id);
}
