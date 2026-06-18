"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/ui/metric-card";
import { StatusBadge } from "@/components/ui/status-badge";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { Document, Journal } from "@/types";
import {
  Shield,
  FileText,
  CheckCircle2,
  AlertCircle,
  ChevronRight,
  BookOpen,
  BarChart3,
} from "lucide-react";
import Link from "next/link";

const JOURNAL_LIST: Journal[] = [
  { id: "ieee", name: "IEEE", shortName: "IEEE", citationStyle: "IEEE", description: "Two-column technical format" },
  { id: "acm", name: "ACM", shortName: "ACM", citationStyle: "ACM", description: "Computer science proceedings" },
  { id: "springer", name: "Springer LNCS", shortName: "Springer", citationStyle: "Springer", description: "Lecture Notes in CS" },
  { id: "elsevier", name: "Elsevier", shortName: "Elsevier", citationStyle: "Elsevier", description: "Scientific journal format" },
  { id: "apa", name: "APA 7th", shortName: "APA", citationStyle: "APA", description: "Social sciences" },
  { id: "mla", name: "MLA 9th", shortName: "MLA", citationStyle: "MLA", description: "Humanities formatting" },
  { id: "nature", name: "Nature", shortName: "Nature", citationStyle: "Nature", description: "Single-column scientific" },
];

export default function CompliancePage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedJournal, setSelectedJournal] = useState<string | null>(null);

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

  const docsWithCompliance = documents.filter((d) => d.compliance_report);
  const totalChecks = docsWithCompliance.reduce(
    (sum, d) => sum + (d.compliance_report?.checks_performed || 0),
    0
  );
  const totalPassed = docsWithCompliance.reduce(
    (sum, d) => sum + (d.compliance_report?.checks_passed || 0),
    0
  );

  if (loading) return <LoadingState message="Loading compliance data..." />;
  if (error) return <ErrorState message={error} onRetry={fetchDocuments} />;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">
          Journal Compliance
        </h1>
        <p className="text-muted-foreground mt-1 font-medium">
          Validate your manuscript against journal requirements.
        </p>
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
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {JOURNAL_LIST.map((journal) => (
              <button
                key={journal.id}
                onClick={() =>
                  setSelectedJournal(selectedJournal === journal.id ? null : journal.id)
                }
                className={`text-left p-3 rounded-lg border-2 transition-all ${
                  selectedJournal === journal.id
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50 hover:bg-muted/50"
                }`}
              >
                <p className="text-xs font-semibold text-primary uppercase tracking-wider">
                  {journal.shortName}
                </p>
                <p className="text-sm font-medium text-foreground mt-1">{journal.name}</p>
                <p className="text-xs text-muted-foreground mt-0.5">
                  Style: {journal.citationStyle}
                </p>
              </button>
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
              description="Upload a manuscript to check compliance."
              action={{
                label: "Upload Document",
                onClick: () => (window.location.href = "/dashboard"),
              }}
            />
          ) : (
            <div className="space-y-3">
              {documents.map((doc) => {
                const report = doc.compliance_report;
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
                        <p className="text-sm font-medium text-foreground truncate">
                          {doc.filename}
                        </p>
                        <div className="flex items-center gap-3 mt-1">
                          <StatusBadge status={doc.status} />
                          {report && (
                            <span className="text-xs text-muted-foreground">
                              Score: {report.score?.overall ?? "—"}% |{" "}
                              {report.checks_passed}/{report.checks_performed} passed
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
          <CardTitle className="text-sm">About Compliance Checking</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Compliance analysis validates your manuscript against journal-specific requirements
            including word count, abstract length, reference count, citation style, figure limits,
            and section structure. Each check produces a pass, warn, or fail status with actionable
            recommendations.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
