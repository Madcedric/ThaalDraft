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
import {
  Palette,
  FileText,
  CheckCircle2,
  ChevronRight,
  Download,
  Eye,
} from "lucide-react";
import Link from "next/link";

const FORMAT_LIST = [
  { id: "ieee", name: "IEEE", description: "Two-column technical format" },
  { id: "acm", name: "ACM", description: "Conference proceedings" },
  { id: "springer", name: "Springer LNCS", description: "Lecture Notes in CS" },
  { id: "elsevier", name: "Elsevier", description: "Scientific journal" },
  { id: "apa", name: "APA 7th", description: "Social sciences" },
  { id: "mla", name: "MLA 9th", description: "Humanities" },
  { id: "nature", name: "Nature", description: "Single-column scientific" },
];

export default function FormattingPage() {
  const { user } = useAuth();
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedFormat, setSelectedFormat] = useState<string | null>(null);

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

  const formattedDocs = documents.filter((d) => d.status === "formatted");

  if (loading) return <LoadingState message="Loading formatting data..." />;
  if (error) return <ErrorState message={error} onRetry={fetchDocuments} />;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">
          Formatting Studio
        </h1>
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
          value={FORMAT_LIST.length}
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
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
            {FORMAT_LIST.map((fmt) => (
              <button
                key={fmt.id}
                onClick={() =>
                  setSelectedFormat(selectedFormat === fmt.id ? null : fmt.id)
                }
                className={`text-left p-3 rounded-lg border-2 transition-all ${
                  selectedFormat === fmt.id
                    ? "border-primary bg-primary/5"
                    : "border-border hover:border-primary/50 hover:bg-muted/50"
                }`}
              >
                <p className="text-xs font-semibold text-primary uppercase tracking-wider">
                  {fmt.id}
                </p>
                <p className="text-sm font-medium text-foreground mt-1">{fmt.name}</p>
                <p className="text-xs text-muted-foreground mt-0.5">{fmt.description}</p>
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
              description="Upload a manuscript to format it."
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
                        {doc.status === "formatted" && (
                          <span className="text-xs text-muted-foreground flex items-center gap-1">
                            <Download className="w-3 h-3" /> Ready
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
          <CardTitle className="text-sm">About Formatting Studio</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            The Formatting Studio converts your structured manuscript into publication-ready
            formats. Choose from 7 journal templates (IEEE, ACM, Springer, Elsevier, APA,
            MLA, Nature) and export as DOCX or PDF. Each template applies correct margins,
            fonts, heading styles, and citation formatting.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
