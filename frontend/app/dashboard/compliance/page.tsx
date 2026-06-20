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
import { Document, JournalRule, ComplianceReport } from "@/types";
import {
  Shield,
  FileText,
  CheckCircle2,
  AlertCircle,
  ChevronRight,
  BarChart3,
  Loader2,
} from "lucide-react";
import Link from "next/link";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function CompliancePage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [journals, setJournals] = useState<JournalRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedJournal, setSelectedJournal] = useState<string | null>(null);
  const [analyzing, setAnalyzing] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const token = await user.getIdToken();
      const [docsRes, journalsRes] = await Promise.all([
        fetch(`${API_BASE}/api/v1/documents/?limit=50`, { headers: { Authorization: `Bearer ${token}` } }),
        fetch(`${API_BASE}/api/v1/documents/compliance/journals`, { headers: { Authorization: `Bearer ${token}` } }),
      ]);
      if (!docsRes.ok) throw new Error("Failed to fetch documents");
      const docsData = await docsRes.json();
      setDocuments(docsData.documents || []);

      if (journalsRes.ok) {
        const journalsData = await journalsRes.json();
        setJournals(journalsData.journals || []);
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

  const getComplianceReport = (doc: Document): ComplianceReport | undefined => {
    const parsed = doc.parsed_json as Record<string, unknown> | undefined;
    return parsed?.compliance_report as ComplianceReport | undefined;
  };

  const handleAnalyze = async (docId: string, journalId: string) => {
    if (!user) return;
    setAnalyzing(docId);
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${API_BASE}/api/v1/documents/${docId}/compliance/analyze`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ journal_id: journalId }),
      });
      if (!response.ok) throw new Error("Analysis failed");
      await fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : "Analysis failed");
    } finally {
      setAnalyzing(null);
    }
  };

  const docsWithCompliance = documents.filter((d) => getComplianceReport(d));
  const totalChecks = docsWithCompliance.reduce(
    (sum, d) => sum + (getComplianceReport(d)?.checks_performed || 0), 0
  );
  const totalPassed = docsWithCompliance.reduce(
    (sum, d) => sum + (getComplianceReport(d)?.checks_passed || 0), 0
  );

  if (loading) return <LoadingState message="Loading compliance data..." />;
  if (error) return <ErrorState message={error} onRetry={fetchData} />;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">Journal Compliance</h1>
        <p className="text-muted-foreground mt-1 font-medium">Validate your manuscript against journal requirements.</p>
      </div>

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Documents"
          value={docsWithCompliance.length}
          icon={FileText}
          description="Compliance checked"
        />
        <MetricCard
          label="Checks Run"
          value={totalChecks}
          icon={BarChart3}
          description="Total validations"
        />
        <MetricCard
          label="Checks Passed"
          value={totalPassed}
          icon={CheckCircle2}
          description="Passed validations"
        />
        <MetricCard
          label="Pass Rate"
          value={totalChecks > 0 ? `${Math.round((totalPassed / totalChecks) * 100)}%` : "—"}
          icon={Shield}
          description="Overall compliance"
        />
      </div>

      {/* Supported Journals */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Supported Journals</CardTitle>
        </CardHeader>
        <CardContent>
          {journals.length === 0 ? (
            <p className="text-sm text-muted-foreground">No journals available.</p>
          ) : (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
              {journals.map((journal) => (
                <button
                  key={journal.journal_id}
                  onClick={() => setSelectedJournal(selectedJournal === journal.journal_id ? null : journal.journal_id)}
                  className={`text-left p-3 rounded-lg border-2 transition-all ${
                    selectedJournal === journal.journal_id
                      ? "border-primary bg-primary/5"
                      : "border-border hover:border-primary/50 hover:bg-muted/50"
                  }`}
                >
                  <p className="text-xs font-semibold text-primary uppercase tracking-wider">
                    {journal.journal_id}
                  </p>
                  <p className="text-sm font-medium text-foreground mt-1">{journal.journal_name}</p>
                  <p className="text-xs text-muted-foreground mt-0.5">
                    Style: {journal.citation_style}
                  </p>
                  <p className="text-xs text-muted-foreground mt-0.5 line-clamp-2">
                    {journal.description}
                  </p>
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
              description="Upload a manuscript to check compliance."
              action={{
                label: "Upload Document",
                onClick: () => (window.location.href = "/dashboard"),
              }}
            />
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => {
                const report = getComplianceReport(doc);
                return (
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
                          {report && (
                            <span className="text-xs text-muted-foreground">
                              Score: {report.score?.overall ?? "—"}% |{" "}
                              {report.checks_passed}/{report.checks_performed} passed
                            </span>
                          )}
                          {!report && (
                            <span className="text-xs text-muted-foreground italic">
                              No compliance report
                            </span>
                          )}
                        </div>
                      </div>
                    </Link>
                    {selectedJournal && (
                      <Button
                        size="sm"
                        variant="outline"
                        onClick={() => handleAnalyze(doc.id, selectedJournal)}
                        disabled={analyzing === doc.id}
                        className="ml-3 shrink-0"
                      >
                        {analyzing === doc.id ? (
                          <Loader2 className="w-3 h-3 animate-spin mr-1" />
                        ) : null}
                        Check
                      </Button>
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
          <CardTitle className="text-sm">About Compliance Checking</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Compliance analysis validates your manuscript against journal-specific requirements
            including word count, abstract length, reference count, citation style, figure limits,
            and section structure. Select a journal above, then click &quot;Check&quot; on any document
            to run the analysis.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
