"use client";

import { useState } from "react";
import { useParams } from "next/navigation";
import { useDocument } from "@/hooks/use-document";
import { enqueueJob } from "@/services/api";
import { useAuth } from "@/lib/auth-context";
import { formatDate, getStatusColor, getJobTypeLabel } from "@/utils/helpers";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Loader2, AlertCircle, FileText, RefreshCw } from "lucide-react";

export default function DocumentPage() {
  const { user } = useAuth();
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

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 className="w-6 h-6 animate-spin text-muted-foreground" />
      </div>
    );
  }

  if (error) {
    return (
      <Alert variant="destructive" className="max-w-4xl mx-auto mt-8">
        <AlertCircle className="h-4 w-4" />
        <AlertDescription>{error}</AlertDescription>
      </Alert>
    );
  }

  if (!doc) {
    return (
      <div className="text-center py-20 text-muted-foreground">
        No document loaded.
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold tracking-tight text-foreground">{doc.filename}</h2>
          <p className="text-sm text-muted-foreground mt-1">Document ID: {doc.id}</p>
        </div>
        <Badge variant="outline" className={getStatusColor(doc.status)}>
          {doc.status}
        </Badge>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Document Info</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2 text-sm">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Filename</span>
              <span className="font-medium">{doc.filename}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Status</span>
              <span className={`font-medium ${getStatusColor(doc.status)}`}>{doc.status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Created</span>
              <span className="font-medium">{formatDate(doc.created_at)}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Actions</CardTitle>
          </CardHeader>
          <CardContent>
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
              <p className="text-sm text-destructive mt-2">{enqueueError}</p>
            )}
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Processing Jobs</CardTitle>
        </CardHeader>
        <CardContent>
          {jobs.length === 0 ? (
            <p className="text-sm text-muted-foreground">No jobs yet.</p>
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
                  <Badge variant="outline" className={getStatusColor(job.status)}>
                    {job.status}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {(doc.parsed_json || doc.structured_json) && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {doc.parsed_json && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Parsed Content</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-xs whitespace-pre-wrap max-h-64 overflow-auto bg-muted p-3 rounded-lg">
                  {JSON.stringify(doc.parsed_json, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
          {doc.structured_json && (
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Structured Data</CardTitle>
              </CardHeader>
              <CardContent>
                <pre className="text-xs whitespace-pre-wrap max-h-64 overflow-auto bg-muted p-3 rounded-lg">
                  {JSON.stringify(doc.structured_json, null, 2)}
                </pre>
              </CardContent>
            </Card>
          )}
        </div>
      )}
    </div>
  );
}
