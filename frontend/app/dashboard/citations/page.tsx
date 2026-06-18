"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { Document } from "@/types";
import { BookOpen, FileText, CheckCircle2, AlertCircle, ChevronRight } from "lucide-react";
import Link from "next/link";

export default function CitationsPage() {
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
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"}/api/v1/documents/?limit=50`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) {
        throw new Error("Failed to fetch documents");
      }
      const data = await response.json();
      setDocuments(data.documents || []);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to load documents";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  const docsWithCitations = documents.filter(
    (doc) => doc.structured_json?.citations && (doc.structured_json.citations as string[]).length > 0
  );

  const totalCitations = docsWithCitations.reduce(
    (sum, doc) => sum + ((doc.structured_json?.citations as string[]) || []).length,
    0
  );

  const totalReferences = docsWithCitations.reduce(
    (sum, doc) => sum + ((doc.structured_json?.references as unknown[]) || []).length,
    0
  );

  if (loading) {
    return <LoadingState message="Loading citation data..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchDocuments} />;
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">Citation Center</h1>
        <p className="text-muted-foreground mt-1 font-medium">Analyze and validate your manuscript citations.</p>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Documents"
          value={docsWithCitations.length}
          icon={FileText}
          description="With citations"
        />
        <MetricCard
          label="Total Citations"
          value={totalCitations}
          icon={BookOpen}
          description="In-text references"
        />
        <MetricCard
          label="Total References"
          value={totalReferences}
          icon={CheckCircle2}
          description="Bibliography entries"
        />
        <MetricCard
          label="Health Score"
          value="—"
          icon={AlertCircle}
          description="Run analysis first"
        />
      </div>

      {/* Documents with Citations */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Documents</CardTitle>
        </CardHeader>
        <CardContent>
          {documents.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No documents yet"
              description="Upload a manuscript to analyze its citations."
              action={{
                label: "Upload Document",
                onClick: () => (window.location.href = "/dashboard"),
              }}
            />
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => {
                const citations = (doc.structured_json?.citations as string[]) || [];
                const references = (doc.structured_json?.references as unknown[]) || [];
                const hasCitations = citations.length > 0;

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
                          {hasCitations && (
                            <span className="text-xs text-muted-foreground">
                              {citations.length} citations / {references.length} references
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
          <CardTitle className="text-sm">About Citation Analysis</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Citation analysis helps you identify issues with your references and in-text citations.
            The engine detects numeric and author-year citation styles, validates references against
            external databases (CrossRef, OpenAlex), and provides a health score for your manuscript.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
