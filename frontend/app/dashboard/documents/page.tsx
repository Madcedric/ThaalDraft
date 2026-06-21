"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatusBadge } from "@/components/ui/status-badge";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { formatDate, formatFileSize, getFileTypeFromFilename } from "@/utils/helpers";
import { Document } from "@/types";
import { FileText, Clock, ChevronRight, Upload, AlertCircle } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";

export default function DocumentsPage() {
  const { user } = useAuth();
  const router = useRouter();
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

  if (loading) {
    return <LoadingState message="Loading documents..." />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchDocuments} />;
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">Documents</h1>
          <p className="text-muted-foreground mt-1 font-medium">Manage your manuscripts and track processing status.</p>
        </div>
        <Link href="/dashboard">
          <Button>
            <Upload className="w-4 h-4 mr-2" />
            Upload New
          </Button>
        </Link>
      </div>

      {documents.length === 0 ? (
        <Card>
          <CardContent className="p-0">
            <EmptyState
              icon={FileText}
              title="No documents yet"
              description="Upload your first manuscript to begin the publication process."
              action={{
                label: "Upload Manuscript",
                onClick: () => router.push("/dashboard"),
              }}
            />
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-3">
          {documents.map((doc) => (
            <Link
              key={doc.id}
              href={`/workspace/${doc.id}`}
              className="block"
            >
              <Card className="hover:shadow-md transition-shadow cursor-pointer">
                <CardContent className="p-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 min-w-0">
                      <div className="p-3 bg-muted rounded-xl shrink-0">
                        <FileText className="w-5 h-5 text-muted-foreground" />
                      </div>
                      <div className="min-w-0">
                        <h3 className="text-sm font-semibold text-foreground truncate">{doc.filename}</h3>
                        <div className="flex items-center gap-4 mt-1">
                          <div className="flex items-center gap-1.5">
                            <Clock className="w-3 h-3 text-muted-foreground" />
                            <span className="text-xs text-muted-foreground">{formatDate(doc.created_at)}</span>
                          </div>
                          <span className="text-xs text-muted-foreground">
                            {getFileTypeFromFilename(doc.filename)}
                          </span>
                          {doc.size_bytes && (
                            <span className="text-xs text-muted-foreground">
                              {formatFileSize(doc.size_bytes)}
                            </span>
                          )}
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <StatusBadge status={doc.status} />
                      <ChevronRight className="w-4 h-4 text-muted-foreground" />
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
}

function Button({ children, className, ...props }: React.ButtonHTMLAttributes<HTMLButtonElement> & { children: React.ReactNode }) {
  return (
    <button
      className={`inline-flex items-center justify-center rounded-lg bg-primary px-4 py-2 text-sm font-medium text-primary-foreground shadow-sm hover:bg-primary/90 transition-colors ${className || ""}`}
      {...props}
    >
      {children}
    </button>
  );
}
