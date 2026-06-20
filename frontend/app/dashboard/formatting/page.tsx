"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { Button } from "@/components/ui/button";
import { Document, FormatTemplate } from "@/types";
import {
  Palette,
  FileText,
  CheckCircle2,
  ChevronRight,
  Download,
  Loader2,
} from "lucide-react";
import { exportDocument } from "@/services/api";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function FormattingPage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [templates, setTemplates] = useState<FormatTemplate[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<string | null>(null);
  const [formatting, setFormatting] = useState<string | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const token = await user.getIdToken();
      const [docsRes, templatesRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/documents/?limit=50`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE}/api/v1/formatting/templates`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (!docsRes.ok) throw new Error("Failed to fetch documents");
      const docsData = await docsRes.json();
      setDocuments(docsData.documents || []);

      if (templatesRes.ok) {
        const templatesData = await templatesRes.json();
        setTemplates(templatesData.templates || []);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load data");
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  const handleFormat = async (docId: string, templateId: string) => {
    if (!user) return;
    setFormatting(docId);
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${API_BASE}/api/v1/documents/${docId}/formatting/format`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ template_id: templateId, export_type: "docx" }),
      });
      if (!response.ok) throw new Error("Formatting failed");
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Formatting failed");
    } finally {
      setFormatting(null);
    }
  };

  const formattedDocs = documents.filter((d) => d.status === "formatted");

  const handleDownload = async (docId: string, filename: string, templateId: string) => {
    if (!user) return;
    setDownloading(docId);
    try {
      const token = await user.getIdToken();
      const { blob, filename: serverFilename } = await exportDocument(docId, templateId, "docx", token);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = serverFilename || `${filename.replace(/\.[^.]+$/, "")}_${templateId}.docx`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch {
      setError("Download failed");
    } finally {
      setDownloading(null);
    }
  };

  if (loading) return <LoadingState message="Loading formatting data..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">Formatting Studio</h1>
        <p className="text-muted-foreground mt-1 font-medium">
          Convert your manuscript to publication-ready formats.
        </p>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Documents"
          value={documents.length}
          icon={FileText}
          description="Available for formatting"
        />
        <MetricCard
          label="Formatted"
          value={formattedDocs.length}
          icon={CheckCircle2}
          description="Export ready"
        />
        <MetricCard
          label="Templates"
          value={templates.length}
          icon={Palette}
          description="Format styles"
        />
        <MetricCard
          label="Export Formats"
          value="2"
          icon={Download}
          description="DOCX and PDF"
        />
      </div>

      {/* Format Templates */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Available Templates</CardTitle>
        </CardHeader>
        <CardContent>
          {templates.length === 0 ? (
            <p className="text-sm text-muted-foreground">No templates available.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {templates.map((tpl) => (
                <button
                  key={tpl.id}
                  onClick={() => setSelectedFormat(selectedFormat === tpl.id ? null : tpl.id)}
                  className={`text-left p-3 rounded-lg border-2 transition-all ${
                    selectedFormat === tpl.id
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-primary/50 hover:bg-muted/50"
                  }`}
                >
                  <p className="text-xs font-semibold text-primary uppercase tracking-wider">{tpl.id}</p>
                  <p className="text-sm font-medium text-foreground mt-1">{tpl.name}</p>
                  <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">{tpl.description}</p>
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Documents */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Documents</CardTitle>
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No documents yet"
              description="Upload a manuscript to format it."
              action={{
                label: "Upload Document",
                onClick: () => (window.location.href = "/dashboard"),
              }}
            />
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => (
                <div
                  key={doc.id}
                  className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors group"
                >
                  <Link href={`/dashboard/document/${doc.id}`} className="flex items-center gap-3 min-w-0 flex-1">
                    <div className="p-2 bg-muted rounded-lg shrink-0">
                      <FileText className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">{doc.filename}</p>
                      <div className="flex items-center gap-3 mt-1">
                        <StatusBadge status={doc.status} />
                        {doc.status === "formatted" && (
                          <span className="text-xs text-muted-foreground flex items-center gap-1">
                            <Download className="w-3 h-3" /> Ready
                          </span>
                        )}
                      </div>
                    </div>
                  </Link>
                  {selectedFormat && doc.status !== "formatted" && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleFormat(doc.id, selectedFormat)}
                      disabled={formatting === doc.id}
                      className="ml-3 shrink-0"
                    >
                      {formatting === doc.id ? (
                        <Loader2 className="w-3 h-3 animate-spin mr-1" />
                      ) : null}
                      Format
                    </Button>
                  )}
                  {doc.status === "formatted" && (
                    <Button
                      size="sm"
                      variant="default"
                      onClick={() => handleDownload(doc.id, doc.filename, selectedFormat || "ieee")}
                      disabled={downloading === doc.id}
                      className="ml-3 shrink-0"
                    >
                      {downloading === doc.id ? (
                        <Loader2 className="w-3 h-3 animate-spin mr-1" />
                      ) : (
                        <Download className="w-3 h-3 mr-1" />
                      )}
                      Download DOCX
                    </Button>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">About Formatting Studio</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            The Formatting Studio converts your structured manuscript into publication-ready
            formats. Choose from journal templates (IEEE, ACM, Springer, Elsevier, APA,
            MLA, Nature) and export as DOCX or PDF. Each template applies correct margins,
            fonts, heading styles, and citation formatting. Select a template above, then
            click &quot;Format&quot; on any document.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
