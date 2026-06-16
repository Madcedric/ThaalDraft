"use client";

import { useState, useEffect, Suspense, useCallback } from "react";
import { useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";
import { usePlagiarism } from "@/hooks/use-plagiarism";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { MetricCard } from "@/components/ui/metric-card";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { formatDate } from "@/utils/helpers";
import { Document } from "@/types";
import { FileText, Shield, AlertCircle, CheckCircle2 } from "lucide-react";

function ReportsContent() {
  const { user } = useAuth();
  const { reports, loading, error, fetchReports } = usePlagiarism();
  const searchParams = useSearchParams();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);
  const [selectedDocId, setSelectedDocId] = useState("");

  const fetchDocuments = useCallback(async () => {
    if (!user) return;
    setLoadingDocs(true);
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"}/api/v1/documents/?limit=50`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setDocuments(data.documents || []);
      }
    } catch {
      console.warn("Failed to fetch documents");
    } finally {
      setLoadingDocs(false);
    }
  }, [user]);

  useEffect(() => {
    fetchDocuments();
  }, [fetchDocuments]);

  useEffect(() => {
    const docId = searchParams.get("docId");
    if (docId) {
      setSelectedDocId(docId);
      fetchReports(docId);
    }
  }, [searchParams, fetchReports]);

  const handleDocSelect = (docId: string) => {
    setSelectedDocId(docId);
    if (docId) {
      fetchReports(docId);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">Reports</h1>
        <p className="text-muted-foreground mt-1 font-medium">Analyze document similarity and originality.</p>
      </div>

      {/* Document Selector */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Select Document</CardTitle>
        </CardHeader>
        <CardContent>
          {loadingDocs ? (
            <LoadingState message="Loading documents..." />
          ) : documents.length === 0 ? (
            <EmptyState
              icon={FileText}
              title="No documents available"
              description="Upload a document first to view plagiarism reports."
            />
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {documents.map((doc) => (
                <button
                  key={doc.id}
                  onClick={() => handleDocSelect(doc.id)}
                  className={`text-left p-3 rounded-xl border-2 transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring ${
                    selectedDocId === doc.id
                      ? "border-primary bg-primary/5 shadow-md"
                      : "border-border hover:border-primary/50 hover:bg-muted/50 shadow-sm"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className="p-2 bg-muted rounded-lg shrink-0">
                      <FileText className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">{doc.filename}</p>
                      <StatusBadge status={doc.status} className="mt-1" />
                    </div>
                  </div>
                </button>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Error Display */}
      {error && (
        <ErrorState message={error} onRetry={() => selectedDocId && fetchReports(selectedDocId)} />
      )}

      {/* Reports Display */}
      {reports && selectedDocId && (
        <div className="space-y-4">
          {reports.length === 0 ? (
            <Card>
              <CardContent className="p-0">
                <EmptyState
                  icon={Shield}
                  title="No plagiarism reports"
                  description="Run a plagiarism check on this document to see results."
                />
              </CardContent>
            </Card>
          ) : (
            reports.map((report) => {
              const similarityScore = report.similarity_score ?? 0;
              const similarityPercent = Math.round(similarityScore * 100);
              const isHighSimilarity = similarityPercent > 30;
              const isMediumSimilarity = similarityPercent > 10 && similarityPercent <= 30;

              return (
                <Card key={report.id}>
                  <CardHeader>
                    <CardTitle className="text-sm flex items-center justify-between">
                      <span>Plagiarism Report</span>
                      <span className="text-muted-foreground font-normal text-xs">
                        {formatDate(report.created_at)}
                      </span>
                    </CardTitle>
                  </CardHeader>
                  <CardContent className="space-y-4">
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                      <MetricCard
                        label="Similarity Score"
                        value={`${similarityPercent}%`}
                        icon={Shield}
                        description={isHighSimilarity ? "High similarity detected" : isMediumSimilarity ? "Moderate similarity" : "Low similarity"}
                      />
                      <MetricCard
                        label="Status"
                        value={isHighSimilarity ? "Review Needed" : "Looks Good"}
                        icon={isHighSimilarity ? AlertCircle : CheckCircle2}
                        description={isHighSimilarity ? "Manual review recommended" : "No major concerns"}
                      />
                      <MetricCard
                        label="Report ID"
                        value={report.id.slice(0, 8)}
                        icon={FileText}
                        description="Unique identifier"
                      />
                    </div>

                    {/* Similarity Progress */}
                    <div className="space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="text-sm font-medium text-foreground">Similarity Level</span>
                        <StatusBadge
                          status={isHighSimilarity ? "failed" : isMediumSimilarity ? "processing" : "completed"}
                          label={isHighSimilarity ? "High" : isMediumSimilarity ? "Medium" : "Low"}
                        />
                      </div>
                      <div className="w-full bg-muted rounded-full h-2.5">
                        <div
                          className={`h-2.5 rounded-full transition-all ${
                            isHighSimilarity ? "bg-red-500" : isMediumSimilarity ? "bg-amber-500" : "bg-emerald-500"
                          }`}
                          style={{ width: `${similarityPercent}%` }}
                        />
                      </div>
                    </div>

                    {/* Report Details */}
                    {report.report && (
                      <div className="rounded-lg bg-muted p-4">
                        <h4 className="text-sm font-medium text-foreground mb-2">Report Details</h4>
                        <pre className="text-xs text-muted-foreground whitespace-pre-wrap overflow-auto max-h-48">
                          {typeof report.report === "string"
                            ? report.report
                            : JSON.stringify(report.report, null, 2)}
                        </pre>
                      </div>
                    )}
                  </CardContent>
                </Card>
              );
            })
          )}
        </div>
      )}
    </div>
  );
}

export default function ReportsPage() {
  return (
    <Suspense
      fallback={
        <div className="flex items-center justify-center py-20">
          <LoadingState message="Loading reports..." />
        </div>
      }
    >
      <ReportsContent />
    </Suspense>
  );
}
