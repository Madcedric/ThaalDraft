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
import { Document, SubmissionPackage } from "@/types";
import { buildSubmissionPackage, getSubmissionPackage, downloadSubmissionZip } from "@/services/api";
import {
  Send,
  FileText,
  CheckCircle2,
  Package,
  Download,
  ChevronRight,
  Loader2,
  FileDown,
} from "lucide-react";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function SubmissionPage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [building, setBuilding] = useState<string | null>(null);
  const [packages, setPackages] = useState<Record<string, { package: SubmissionPackage; total_components: number; completed_components: number }>>({});

  const fetchDocuments = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const token = await user.getIdToken();
      const response = await fetch(
        `${API_BASE}/api/v1/documents/?limit=50`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      if (!response.ok) throw new Error("Failed to fetch documents");
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load documents");
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const handleBuildPackage = async (docId: string, journalId: string = "ieee") => {
    if (!user) return;
    setBuilding(docId);
    setError(null);
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${API_BASE}/api/v1/documents/${docId}/submission/build`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({
          journal_id: journalId,
          components: [
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
      if (!response.ok) throw new Error("Failed to build package");
      const data = await response.json();
      setPackages((prev) => ({ ...prev, [docId]: data.package }));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Build failed");
    } finally {
      setBuilding(null);
    }
  };

  const handleExport = async (docId: string, template: string, format: string) => {
    if (!user) return;
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${API_BASE}/api/v1/documents/${docId}/export`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ template, format }),
      });
      if (!response.ok) throw new Error("Export failed");
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `${docId}_${template}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Export failed");
    }
  };

  const handleDownloadComponent = async (filePath: string, filename: string) => {
    try {
      const blob = new Blob([""], { type: "application/octet-stream" });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Download failed");
    }
  };

  if (loading) return <LoadingState message="Loading submission data..." />;
  if (error) return <ErrorState message={error} onRetry={fetchDocuments} />;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">
          Submission Package
        </h1>
        <p className="text-muted-foreground mt-1 font-medium">
          Generate publication-ready submission packages.
        </p>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Documents"
          value={documents.length}
          icon={FileText}
          description="Ready for submission"
        />
        <MetricCard
          label="Packages Built"
          value={Object.keys(packages).length}
          icon={Package}
          description="Submission packages"
        />
        <MetricCard
          label="Components"
          value="7"
          icon={CheckCircle2}
          description="Per package"
        />
        <MetricCard
          label="Formats"
          value="2"
          icon={Download}
          description="DOCX, PDF"
        />
      </div>

      {/* Package Components */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Package Components</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {[
              { id: "manuscript", name: "Manuscript DOCX", description: "Formatted manuscript" },
              { id: "compliance", name: "Compliance Report", description: "Journal validation" },
              { id: "review", name: "Reviewer Report", description: "AI review feedback" },
              { id: "citation", name: "Citation Report", description: "Citation analysis" },
              { id: "cover", name: "Cover Letter", description: "Editor correspondence" },
              { id: "author", name: "Author Statement", description: "Contributions" },
              { id: "conflict", name: "Conflict Statement", description: "Disclosures" },
            ].map((comp) => (
              <div
                key={comp.id}
                className="p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors"
              >
                <p className="text-xs font-semibold text-primary uppercase tracking-wider">{comp.id}</p>
                <p className="text-sm font-medium text-foreground mt-1">{comp.name}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{comp.description}</p>
              </div>
            ))}
          </div>
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
              description="Upload a manuscript to build a submission package."
              action={{
                label: "Upload Document",
                onClick: () => (window.location.href = "/dashboard"),
              }}
            />
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => {
                const pkg = packages[doc.id];
                return (
                  <div
                    key={doc.id}
                    className="p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors"
                  >
                    <div className="flex items-center justify-between">
                      <Link href={`/dashboard/document/${doc.id}`} className="flex items-center gap-3 min-w-0 flex-1">
                        <div className="p-2 bg-muted rounded-lg shrink-0">
                          <FileText className="w-4 h-4 text-muted-foreground" />
                        </div>
                        <div className="min-w-0">
                          <p className="text-sm font-medium text-foreground truncate">{doc.filename}</p>
                          <div className="flex items-center gap-3 mt-1">
                            <StatusBadge status={doc.status} />
                            {pkg && (
                              <span className="text-xs text-muted-foreground">
                                {pkg.completed_components}/{pkg.total_components} components
                              </span>
                            )}
                          </div>
                        </div>
                      </Link>
                      <div className="flex items-center gap-2 ml-3 shrink-0">
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleBuildPackage(doc.id)}
                          disabled={building === doc.id}
                        >
                          {building === doc.id ? (
                            <Loader2 className="w-3 h-3 animate-spin mr-1" />
                          ) : (
                            <Package className="w-3 h-3 mr-1" />
                          )}
                          Build
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleExport(doc.id, "ieee", "docx")}
                        >
                          <FileDown className="w-3 h-3 mr-1" />
                          DOCX
                        </Button>
                        <Button
                          size="sm"
                          variant="outline"
                          onClick={() => handleExport(doc.id, "ieee", "pdf")}
                        >
                          <FileDown className="w-3 h-3 mr-1" />
                          PDF
                        </Button>
                        {pkg && pkg.package && (
                          <Button
                            size="sm"
                            variant="default"
                            onClick={async () => {
                              if (!user) return;
                              try {
                                const token = await user.getIdToken();
                                const blob = await downloadSubmissionZip(doc.id, token);
                                const url = URL.createObjectURL(blob);
                                const a = document.createElement("a");
                                a.href = url;
                                a.download = `${doc.filename}_submission.zip`;
                                document.body.appendChild(a);
                                a.click();
                                document.body.removeChild(a);
                                URL.revokeObjectURL(url);
                              } catch (err) {
                                setError(err instanceof Error ? err.message : "ZIP download failed");
                              }
                            }}
                          >
                            <Download className="w-3 h-3 mr-1" />
                            ZIP
                          </Button>
                        )}
                      </div>
                    </div>
                    {pkg && pkg.package && pkg.package.components && pkg.package.components.length > 0 && (
                      <div className="mt-2 pl-11 space-y-1">
                        {pkg.package.components.map((comp, i) => (
                          <div key={i} className="flex items-center gap-2 text-xs text-muted-foreground">
                            {comp.status === "completed" ? (
                              <CheckCircle2 className="w-3 h-3 text-green-500" />
                            ) : comp.status === "failed" ? (
                              <span className="w-3 h-3 text-red-500">X</span>
                            ) : (
                              <span className="w-3 h-3">-</span>
                            )}
                            <span>{comp.component}</span>
                            {comp.filename && (
                              <span className="text-muted-foreground/60">({comp.filename})</span>
                            )}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">About Submission Packages</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            The Submission Package Generator compiles all your manuscript artifacts into
            a single submission-ready package. Click &quot;Build&quot; to generate all components
            (formatted manuscript, compliance/review/citation reports, cover letter, author
            statement, and conflict of interest statement). Use &quot;DOCX&quot; or &quot;PDF&quot; to
            export the formatted manuscript directly.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
