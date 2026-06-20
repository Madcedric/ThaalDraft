"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useDocument } from "@/hooks/use-document";
import {
  runStructureAnalysis,
  analyzeCitations,
  analyzeCompliance,
  analyzeReview,
  formatDocument,
  analyzePlagiarism,
  exportDocument,
  getFormatTemplates,
  getJournalRules,
} from "@/services/api";
import { useAuth } from "@/lib/auth-context";
import { formatDate, formatFileSize, getStatusColor, getJobTypeLabel, getFileTypeFromFilename } from "@/utils/helpers";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";
import { MetricCard } from "@/components/ui/metric-card";
import { ConfidenceBadge } from "@/components/ui/confidence-badge";
import { SectionSummaryCard } from "@/components/ui/section-summary-card";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { StructuredData, CitationReport, ComplianceReport, ReviewReport, JournalRule, FormatTemplate } from "@/types";
import {
  Loader2,
  AlertCircle,
  FileText,
  RefreshCw,
  Users,
  Calendar,
  FileType,
  Hash,
  BookOpen,
  ArrowLeft,
  Sparkles,
  Shield,
  MessageSquare,
  Palette,
  CheckCircle2,
  AlertTriangle,
  Download,
} from "lucide-react";
import Link from "next/link";

export default function DocumentPage() {
  const { user } = useAuth();
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;
  const { document: doc, jobs, loading, error, refresh, refreshJobs } = useDocument(id);

  const [runningAnalysis, setRunningAnalysis] = useState<string | null>(null);
  const [analysisError, setAnalysisError] = useState<string | null>(null);

  const runAnalysis = async (
    name: string,
    fn: (token: string) => Promise<unknown>
  ) => {
    if (!user || !id) return;
    setRunningAnalysis(name);
    setAnalysisError(null);
    try {
      const token = await user.getIdToken();
      await fn(token);
      await refresh();
    } catch (err) {
      const message = err instanceof Error ? err.message : `Failed to run ${name}`;
      setAnalysisError(message);
    } finally {
      setRunningAnalysis(null);
    }
  };

  const handleRunStructure = () =>
    runAnalysis("structure", (token) => runStructureAnalysis(id, token));

  const handleRunCitations = () =>
    runAnalysis("citations", (token) => analyzeCitations(id, token));

  const handleRunCompliance = async () => {
    if (!user || !id) return;
    setRunningAnalysis("compliance");
    setAnalysisError(null);
    try {
      const token = await user.getIdToken();
      const { journals } = await getJournalRules(token);
      const journalId = journals.length > 0 ? journals[0].journal_id : "ieee";
      await analyzeCompliance(id, journalId, token);
      await refresh();
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : "Failed to run compliance");
    } finally {
      setRunningAnalysis(null);
    }
  };

  const handleRunReview = () =>
    runAnalysis("review", (token) => analyzeReview(id, token));

  const handleRunFormatting = async () => {
    if (!user || !id) return;
    setRunningAnalysis("formatting");
    setAnalysisError(null);
    try {
      const token = await user.getIdToken();
      await formatDocument(id, "ieee", token);
      await refresh();
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : "Failed to format");
    } finally {
      setRunningAnalysis(null);
    }
  };

  const handleRunPlagiarism = () =>
    runAnalysis("plagiarism", (token) => analyzePlagiarism(id, token));

  const handleExport = async (template: string, format: string) => {
    if (!user || !id) return;
    setRunningAnalysis("export");
    setAnalysisError(null);
    try {
      const token = await user.getIdToken();
      const { blob, filename: serverFilename } = await exportDocument(id, template, format, token);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = serverFilename || `${doc?.filename || id}_${template}.${format}`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    } catch (err) {
      setAnalysisError(err instanceof Error ? err.message : "Export failed");
    } finally {
      setRunningAnalysis(null);
    }
  };

  if (loading) return <LoadingState message="Loading document..." />;
  if (error) return <ErrorState message={error} onRetry={() => router.refresh()} />;
  if (!doc) return <ErrorState message="Document not found." />;

  const structured = (doc.parsed_json || doc.structured_json) as StructuredData | undefined;
  const metadata = structured?.metadata;
  const confidenceReport = structured?.confidence_report;
  const sections = structured?.sections || [];
  const authors = structured?.authors || [];
  const citationReport = (structured as Record<string, unknown>)?.citation_report as CitationReport | undefined;
  const complianceReport = (structured as Record<string, unknown>)?.compliance_report as ComplianceReport | undefined;
  const reviewReport = (structured as Record<string, unknown>)?.review_report as ReviewReport | undefined;
  const plagiarismReport = (structured as Record<string, unknown>)?.plagiarism_report as Record<string, unknown> | undefined;
  const plagiarismMatches = ((plagiarismReport?.matches || []) as Array<{ document_id?: string; score?: number }>);
  const plagiarismMaxScore = plagiarismMatches.length > 0 ? Math.max(...plagiarismMatches.map((m) => m.score || 0)) : 0;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      {/* Back Navigation */}
      <Link
        href="/dashboard/documents"
        className="inline-flex items-center text-sm text-muted-foreground hover:text-foreground transition-colors"
      >
        <ArrowLeft className="w-4 h-4 mr-1" />
        Back to Documents
      </Link>

      {/* Document Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">
            {structured?.title || doc.filename}
          </h1>
          <p className="text-sm text-muted-foreground mt-1">
            Document ID: {doc.id}
          </p>
        </div>
        <StatusBadge status={doc.status} />
      </div>

      {/* Document Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="File Type"
          value={getFileTypeFromFilename(doc.filename)}
          icon={FileType}
        />
        <MetricCard
          label="File Size"
          value={formatFileSize(doc.size_bytes || 0)}
          icon={FileText}
        />
        <MetricCard
          label="Word Count"
          value={metadata?.word_count?.toLocaleString() || "—"}
          icon={Hash}
          description={metadata?.has_abstract ? "Has abstract" : undefined}
        />
        <MetricCard
          label="References"
          value={metadata?.reference_count?.toString() || "—"}
          icon={BookOpen}
          description={metadata?.has_references ? "Detected" : undefined}
        />
      </div>

      {/* Document Info + Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Document Info */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Document Info</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="flex items-center justify-between py-2 border-b border-border">
              <span className="text-sm text-muted-foreground">Filename</span>
              <span className="text-sm font-medium text-foreground">{doc.filename}</span>
            </div>
            <div className="flex items-center justify-between py-2 border-b border-border">
              <span className="text-sm text-muted-foreground">Created</span>
              <span className="text-sm font-medium text-foreground">{formatDate(doc.created_at)}</span>
            </div>
            {authors.length > 0 && (
              <div className="flex items-center justify-between py-2 border-b border-border">
                <span className="text-sm text-muted-foreground">Authors</span>
                <span className="text-sm font-medium text-foreground">
                  {authors.map((a) => a.name).join(", ")}
                </span>
              </div>
            )}
            {confidenceReport?.overall_confidence !== undefined && (
              <div className="flex items-center justify-between py-2">
                <span className="text-sm text-muted-foreground">Detection Confidence</span>
                <ConfidenceBadge confidence={confidenceReport.overall_confidence} />
              </div>
            )}
          </CardContent>
        </Card>

        {/* Actions */}
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Run Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <Button
              onClick={handleRunStructure}
              disabled={!!runningAnalysis}
              className="w-full"
              variant="outline"
              size="sm"
            >
              {runningAnalysis === "structure" ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              Structure Analysis
            </Button>
            <Button
              onClick={handleRunCitations}
              disabled={!!runningAnalysis}
              className="w-full"
              variant="outline"
              size="sm"
            >
              {runningAnalysis === "citations" ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Sparkles className="w-4 h-4 mr-2" />
              )}
              Citation Analysis
            </Button>
            <Button
              onClick={handleRunCompliance}
              disabled={!!runningAnalysis}
              className="w-full"
              variant="outline"
              size="sm"
            >
              {runningAnalysis === "compliance" ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Shield className="w-4 h-4 mr-2" />
              )}
              Compliance Check
            </Button>
            <Button
              onClick={handleRunReview}
              disabled={!!runningAnalysis}
              className="w-full"
              variant="outline"
              size="sm"
            >
              {runningAnalysis === "review" ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <MessageSquare className="w-4 h-4 mr-2" />
              )}
              Reviewer AI
            </Button>
            <Button
              onClick={handleRunFormatting}
              disabled={!!runningAnalysis}
              className="w-full"
              variant="outline"
              size="sm"
            >
              {runningAnalysis === "formatting" ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <Palette className="w-4 h-4 mr-2" />
              )}
              Format Document
            </Button>
            <Button
              onClick={handleRunPlagiarism}
              disabled={!!runningAnalysis}
              className="w-full"
              variant="outline"
              size="sm"
            >
              {runningAnalysis === "plagiarism" ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <AlertTriangle className="w-4 h-4 mr-2" />
              )}
              Plagiarism Check
            </Button>
            <div className="border-t border-border pt-2 mt-1">
              <p className="text-xs font-medium text-muted-foreground mb-2">Export</p>
              <div className="flex gap-2">
                <Button
                  onClick={() => handleExport("ieee", "docx")}
                  disabled={!!runningAnalysis}
                  className="flex-1"
                  variant="default"
                  size="sm"
                >
                  {runningAnalysis === "export" ? (
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4 mr-1" />
                  )}
                  DOCX
                </Button>
                <Button
                  onClick={() => handleExport("ieee", "pdf")}
                  disabled={!!runningAnalysis}
                  className="flex-1"
                  variant="default"
                  size="sm"
                >
                  {runningAnalysis === "export" ? (
                    <Loader2 className="w-4 h-4 mr-1 animate-spin" />
                  ) : (
                    <Download className="w-4 h-4 mr-1" />
                  )}
                  PDF
                </Button>
              </div>
            </div>
            {analysisError && (
              <p className="text-sm text-destructive mt-2">{analysisError}</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Citation Report Summary */}
      {citationReport && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Sparkles className="w-4 h-4" />
              Citation Report
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard
                label="Total Citations"
                value={citationReport.total_citations}
                icon={BookOpen}
              />
              <MetricCard
                label="Total References"
                value={citationReport.total_references}
                icon={FileText}
              />
              <MetricCard
                label="Resolved"
                value={citationReport.resolved_citations}
                icon={CheckCircle2}
              />
              <MetricCard
                label="Health Score"
                value={`${citationReport.health_score?.overall ?? 0}%`}
                icon={AlertTriangle}
              />
            </div>
            {citationReport.issues.length > 0 && (
              <div className="mt-3">
                <p className="text-xs font-medium text-muted-foreground mb-1">Issues Found</p>
                <div className="space-y-1">
                  {citationReport.issues.slice(0, 5).map((issue, i) => (
                    <p key={i} className="text-xs text-muted-foreground">
                      <span className={`font-medium ${issue.severity === "error" ? "text-destructive" : issue.severity === "warning" ? "text-yellow-500" : ""}`}>
                        {issue.severity.toUpperCase()}:
                      </span>{" "}
                      {issue.message}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Compliance Report Summary */}
      {complianceReport && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <Shield className="w-4 h-4" />
              Compliance Report — {complianceReport.journal_name}
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard
                label="Overall Score"
                value={`${complianceReport.score?.overall ?? 0}%`}
                icon={Shield}
              />
              <MetricCard
                label="Checks Performed"
                value={complianceReport.checks_performed}
                icon={Hash}
              />
              <MetricCard
                label="Passed"
                value={complianceReport.checks_passed}
                icon={CheckCircle2}
              />
              <MetricCard
                label="Failed"
                value={complianceReport.checks_failed}
                icon={AlertTriangle}
              />
            </div>
            {complianceReport.issues.length > 0 && (
              <div className="mt-3">
                <p className="text-xs font-medium text-muted-foreground mb-1">Issues Found</p>
                <div className="space-y-1">
                  {complianceReport.issues.slice(0, 5).map((issue, i) => (
                    <p key={i} className="text-xs text-muted-foreground">
                      <span className={`font-medium ${issue.status === "fail" ? "text-destructive" : issue.status === "warn" ? "text-yellow-500" : "text-green-500"}`}>
                        {issue.status.toUpperCase()}:
                      </span>{" "}
                      {issue.message}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Review Report Summary */}
      {reviewReport && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Review Report
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard
                label="Readiness"
                value={`${reviewReport.publication_readiness?.overall ?? 0}%`}
                icon={MessageSquare}
                description={reviewReport.publication_readiness?.label}
              />
              <MetricCard
                label="Critical"
                value={reviewReport.critical_count}
                icon={AlertTriangle}
              />
              <MetricCard
                label="Major"
                value={reviewReport.major_count}
                icon={AlertCircle}
              />
              <MetricCard
                label="Minor"
                value={reviewReport.minor_count}
                icon={CheckCircle2}
              />
            </div>
            {reviewReport.strengths.length > 0 && (
              <div className="mt-3">
                <p className="text-xs font-medium text-muted-foreground mb-1">Strengths</p>
                <div className="space-y-1">
                  {reviewReport.strengths.slice(0, 3).map((s, i) => (
                    <p key={i} className="text-xs text-muted-foreground">
                      <span className="font-medium text-green-500">{s.title}:</span> {s.description}
                    </p>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      )}

      {/* Structure Summary */}
      {sections.length > 0 && (
        <SectionSummaryCard sections={sections} />
      )}

      {/* Plagiarism Report Summary */}
      {plagiarismReport && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm flex items-center gap-2">
              <AlertTriangle className="w-4 h-4" />
              Plagiarism Report
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <MetricCard label="Similar Documents" value={plagiarismMatches.length} icon={FileText} />
              <MetricCard label="Max Similarity" value={`${Math.round(plagiarismMaxScore * 100)}%`} icon={AlertTriangle} />
              <MetricCard label="Corpus Checked" value={plagiarismMatches.length > 0 ? `${plagiarismMatches.length} docs` : "—"} icon={BookOpen} />
              <MetricCard label="Risk Level" value={plagiarismMaxScore > 0.7 ? "High" : plagiarismMaxScore > 0.4 ? "Medium" : "Low"} icon={CheckCircle2} />
            </div>
          </CardContent>
        </Card>
      )}

      {/* Abstract */}
      {structured?.abstract && (
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Abstract</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground leading-relaxed whitespace-pre-wrap">
              {structured.abstract}
            </p>
          </CardContent>
        </Card>
      )}

      {/* Processing Jobs */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Processing History</CardTitle>
        </CardHeader>
        <CardContent>
          {jobs.length === 0 ? (
            <p className="text-sm text-muted-foreground">No processing jobs yet.</p>
          ) : (
            <div className="space-y-2">
              {jobs.map((job) => (
                <div key={job.id} className="flex items-center justify-between p-3 rounded-lg border border-border">
                  <div className="flex items-center gap-3">
                    <FileText className="w-4 h-4 text-muted-foreground" />
                    <div>
                      <p className="text-sm font-medium">{getJobTypeLabel(job.type)}</p>
                      <p className="text-xs text-muted-foreground">{formatDate(job.created_at)}</p>
                    </div>
                  </div>
                  <StatusBadge status={job.status} />
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
