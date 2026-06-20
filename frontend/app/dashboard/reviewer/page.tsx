"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { Document, ReviewReport } from "@/types";
import {
  MessageSquare,
  FileText,
  CheckCircle2,
  AlertTriangle,
  ChevronRight,
  BarChart3,
  AlertCircle,
} from "lucide-react";
import Link from "next/link";

export default function ReviewerPage() {
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

  const getReviewReport = (doc: Document): ReviewReport | undefined => {
    const parsed = doc.parsed_json as Record<string, unknown> | undefined;
    return parsed?.review_report as ReviewReport | undefined;
  };

  const docsWithReviews = documents.filter((d) => getReviewReport(d));
  const avgReadiness =
    docsWithReviews.length > 0
      ? Math.round(
          docsWithReviews.reduce(
            (sum, d) => sum + (getReviewReport(d)?.publication_readiness?.overall || 0),
            0
          ) / docsWithReviews.length
        )
      : 0;
  const totalCritical = docsWithReviews.reduce(
    (sum, d) => sum + (getReviewReport(d)?.critical_count || 0),
    0
  );

  if (loading) return <LoadingState message="Loading reviewer data..." />;
  if (error) return <ErrorState message={error} onRetry={fetchDocuments} />;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">Reviewer AI</h1>
        <p className="text-muted-foreground mt-1 font-medium">
          Get pre-submission review feedback on your manuscripts.
        </p>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Reviewed"
          value={docsWithReviews.length}
          icon={FileText}
          description="Documents reviewed"
        />
        <MetricCard
          label="Avg. Readiness"
          value={`${avgReadiness}%`}
          icon={BarChart3}
          description="Publication score"
        />
        <MetricCard
          label="Critical Issues"
          value={totalCritical}
          icon={AlertTriangle}
          description="Needs attention"
        />
        <MetricCard
          label="Status"
          value={docsWithReviews.length > 0 ? "Active" : "—"}
          icon={CheckCircle2}
          description="Review engine"
        />
      </div>

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
              description="Upload a manuscript to get AI review feedback."
              action={{
                label: "Upload Document",
                onClick: () => (window.location.href = "/dashboard"),
              }}
            />
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => {
                const report = getReviewReport(doc);
                return (
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
                        <p className="text-sm font-medium text-foreground truncate">{doc.filename}</p>
                        <div className="flex items-center gap-3 mt-1">
                          <StatusBadge status={doc.status} />
                          {report && (
                            <span className="text-xs text-muted-foreground">
                              Readiness: {report.publication_readiness?.overall ?? "—"}% |{" "}
                              {report.publication_readiness?.label ?? "—"}
                            </span>
                          )}
                          {!report && (
                            <span className="text-xs text-muted-foreground italic">
                              No review report — run analysis
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <ChevronRight className="w-4 h-4 text-muted-foreground group-hover:text-primary transition-colors shrink-0" />
                  </Link>
                );
              })}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">About Reviewer AI</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            The Reviewer AI analyzes your manuscript across 6 dimensions: writing quality,
            research clarity, methodology, literature coverage, citation completeness, and
            research gaps. It generates a structured review with strengths, weaknesses,
            and improvement suggestions to help you prepare for submission.
            Open a document and click &quot;Reviewer AI&quot; to run the analysis.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
