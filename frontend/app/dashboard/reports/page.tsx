"use client";

import { useState, useEffect, Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { usePlagiarism } from "@/hooks/use-plagiarism";
import { Loader2, AlertCircle } from "lucide-react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Alert, AlertDescription } from "@/components/ui/alert";

function ReportsContent() {
  const [docId, setDocId] = useState("");
  const { reports, loading, error, fetchReports } = usePlagiarism();
  const searchParams = useSearchParams();

  useEffect(() => {
    const q = searchParams.get("docId");
    if (q && q !== docId) {
      const timer = setTimeout(() => fetchReports(q), 0);
      return () => clearTimeout(timer);
    }
  }, [searchParams, docId, fetchReports]);

  return (
    <div className="max-w-3xl mx-auto space-y-6 pb-12">
      <div>
        <h2 className="text-2xl font-semibold tracking-tight text-foreground">Plagiarism Reports</h2>
        <p className="text-muted-foreground mt-1 font-medium">Analyze document similarity and originality.</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Fetch Report</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-2">
            <input
              value={docId}
              onChange={(e) => setDocId(e.target.value)}
              placeholder="Enter Document ID"
              className="flex-1 h-10 px-3 text-sm border border-border rounded-lg bg-background focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary"
            />
            <button
              disabled={!docId || loading}
              onClick={() => fetchReports(docId)}
              className="h-10 px-4 text-sm font-medium bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                "Fetch"
              )}
            </button>
          </div>
        </CardContent>
      </Card>

      {error && (
        <Alert variant="destructive">
          <AlertCircle className="h-4 w-4" />
          <AlertDescription>{error}</AlertDescription>
        </Alert>
      )}

      {reports && (
        <div className="space-y-4">
          {reports.length === 0 && (
            <Card>
              <CardContent className="py-8 text-center text-muted-foreground">
                No reports found for this document.
              </CardContent>
            </Card>
          )}
          {reports.map((r) => (
            <Card key={r.id}>
              <CardHeader>
                <CardTitle className="text-sm flex items-center justify-between">
                  <span>Report: {r.id}</span>
                  <span className="text-muted-foreground font-normal">
                    Similarity: {((r.similarity_score ?? 0) * 100).toFixed(1)}%
                  </span>
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="w-full bg-muted rounded-full h-2 mb-4">
                  <div
                    className="bg-primary h-2 rounded-full transition-all"
                    style={{ width: `${(r.similarity_score ?? 0) * 100}%` }}
                  />
                </div>
                <pre className="text-xs whitespace-pre-wrap bg-muted p-3 rounded-lg max-h-48 overflow-auto">
                  {JSON.stringify(r.report, null, 2)}
                </pre>
              </CardContent>
            </Card>
          ))}
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
          <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
        </div>
      }
    >
      <ReportsContent />
    </Suspense>
  );
}
