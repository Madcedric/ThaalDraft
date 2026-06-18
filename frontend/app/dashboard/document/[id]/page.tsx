"use client";

import { useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { useDocument } from "@/hooks/use-document";
import { enqueueJob } from "@/services/api";
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
import { StructuredData } from "@/types";
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
} from "lucide-react";
import Link from "next/link";

export default function DocumentPage() {
  const { user } = useAuth();
  const router = useRouter();
  const params = useParams();
  const id = params?.id as string;
  const { document: doc, jobs, loading, error, refreshJobs } = useDocument(id);
  const [enqueueing, setEnqueueing] = useState(false);
  const [enqueueError, setEnqueueError] = useState<string | null>(null);

  const handleEnqueuePlagiarism = async () => {
    if (!user || !id) return;
    setEnqueueing(true);
    setEnqueueError(null);
    try {
      const token = await user.getIdToken();
      await enqueueJob(id, "plagiarism", token);
      refreshJobs();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to enqueue job";
      setEnqueueError(message);
    } finally {
      setEnqueueing(false);
    }
  };

  const handleEnqueueStructure = async () => {
    if (!user || !id) return;
    setEnqueueing(true);
    setEnqueueError(null);
    try {
      const token = await user.getIdToken();
      await enqueueJob(id, "structure", token);
      refreshJobs();
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to enqueue job";
      setEnqueueError(message);
    } finally {
      setEnqueueing(false);
    }
  };

  if (loading) {
    return <LoadingState message="Loading document..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={() => router.refresh()} />;
  }

  if (!doc) {
    return <ErrorState message="Document not found." />;
  }

  const structured = (doc.parsed_json || doc.structured_json) as StructuredData | undefined;
  const metadata = structured?.metadata;
  const confidenceReport = structured?.confidence_report;
  const sections = structured?.sections || [];
  const authors = structured?.authors || [];

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
            <CardTitle className="text-sm">Actions</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button
              onClick={handleEnqueueStructure}
              disabled={enqueueing}
              className="w-full"
              variant="outline"
            >
              {enqueueing ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              Run Structure Analysis
            </Button>
            <Button
              onClick={handleEnqueuePlagiarism}
              disabled={enqueueing}
              className="w-full"
            >
              {enqueueing ? (
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              ) : (
                <RefreshCw className="w-4 h-4 mr-2" />
              )}
              Run Plagiarism Check
            </Button>
            {enqueueError && (
              <p className="text-sm text-destructive">{enqueueError}</p>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Structure Summary */}
      {sections.length > 0 && (
        <SectionSummaryCard sections={sections} />
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
