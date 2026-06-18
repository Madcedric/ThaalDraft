"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { Document, SubmissionPackage } from "@/types";
import {
  Send,
  FileText,
  CheckCircle2,
  Package,
  Download,
  ChevronRight,
} from "lucide-react";
import Link from "next/link";

export default function SubmissionPage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchDocuments = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const token = await user.getIdToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"}/api/v1/documents/?limit=50`,
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
          label="Components"
          value="8"
          icon={Package}
          description="Package types"
        />
        <MetricCard
          label="Formats"
          value="3"
          icon={Download}
          description="DOCX, PDF, LaTeX"
        />
        <MetricCard
          label="Reports"
          value="3"
          icon={CheckCircle2}
          description="Compliance, Review, Citation"
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
              { id: "manuscript", name: "Manuscript", description: "DOCX/PDF/LaTeX" },
              { id: "compliance", name: "Compliance Report", description: "Journal validation" },
              { id: "review", name: "Reviewer Report", description: "AI review feedback" },
              { id: "citation", name: "Citation Report", description: "Citation analysis" },
              { id: "cover", name: "Cover Letter", description: "Editor correspondence" },
              { id: "author", name: "Author Statement", description: "Contributions" },
              { id: "conflict", name: "Conflict Statement", description: "Disclosures" },
              { id: "zip", name: "ZIP Package", description: "All files bundled" },
            ].map((comp) => (
              <div
                key={comp.id}
                className="p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors"
              >
                <p className="text-xs font-semibold text-primary uppercase tracking-wider">
                  {comp.id}
                </p>
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
              {documents.map((doc) => (
                <Link
                  key={doc.id}
                  href={`/dashboard/document/${doc.id}`}
                  className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors group"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 bg-muted rounded-lg shrink-0">
                      <FileText className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">
                        {doc.filename}
                      </p>
                      <div className="flex items-center gap-3 mt-1">
                        <StatusBadge status={doc.status} />
                        {doc.selected_journal && (
                          <span className="text-xs text-muted-foreground">
                            Journal: {doc.selected_journal}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors shrink-0" />
                </Link>
              ))}
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
            a single submission-ready package. It includes the formatted manuscript, compliance
            and review reports, citation analysis, cover letter, author contributions, and
            conflict of interest statement. All files are bundled for easy submission.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
