"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/ui/metric-card";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { Button } from "@/components/ui/button";
import { BatchJob } from "@/types";
import {
  Layers,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Play,
  Plus,
  Upload,
  Loader2,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function BatchPage() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<BatchJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const fetchJobs = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${API_BASE}/api/v1/batch/jobs`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Failed to fetch batch jobs");
      const data = await response.json();
      setJobs(data.jobs || []);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load batch jobs");
    } finally {
      setLoading(false);
    }
  }, [user]);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const handleCreateBatch = async (files: FileList | null) => {
    if (!user || !files || files.length === 0) return;
    setUploading(true);
    setUploadProgress(`Uploading ${files.length} files...`);
    setError(null);
    try {
      const token = await user.getIdToken();
      const fileArray = Array.from(files);
      const uploadedDocIds: string[] = [];

      for (let i = 0; i < fileArray.length; i++) {
        const file = fileArray[i];
        setUploadProgress(`Uploading ${i + 1}/${fileArray.length}: ${file.name}`);
        const formData = new FormData();
        formData.append("file", file);
        const res = await fetch(`${API_BASE}/api/v1/documents/upload`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}` },
          body: formData,
        });
        if (res.ok) {
          const data = await res.json();
          uploadedDocIds.push(data.document_id);
        }
      }

      if (uploadedDocIds.length > 0) {
        setUploadProgress(`Creating batch with ${uploadedDocIds.length} documents...`);
        const batchRes = await fetch(`${API_BASE}/api/v1/batch/create`, {
          method: "POST",
          headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
          body: JSON.stringify({
            document_ids: uploadedDocIds,
            job_type: "full_analysis",
            batch_name: `Batch - ${new Date().toLocaleDateString()}`,
          }),
        });
        if (batchRes.ok) {
          setUploadProgress("Batch created! Starting processing...");
          const batchData = await batchRes.json();
          const batchId = batchData.job_id || batchData.id;
          if (batchId) {
            await fetch(`${API_BASE}/api/v1/batch/${batchId}/start`, {
              method: "POST",
              headers: { Authorization: `Bearer ${token}` },
            });
          }
          await fetchJobs();
        }
      }
      setUploadProgress(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Batch creation failed");
      setUploadProgress(null);
    } finally {
      setUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = "";
    }
  };

  const runningJobs = jobs.filter((j) => j.status === "running");
  const completedJobs = jobs.filter((j) => j.status === "completed");
  const failedJobs = jobs.filter((j) => j.status === "failed");
  const totalFiles = jobs.reduce((sum, j) => sum + j.total_files, 0);

  if (loading) return <LoadingState message="Loading batch data..." />;
  if (error) return <ErrorState message={error} onRetry={fetchJobs} />;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">
            Batch Processing
          </h1>
          <p className="text-muted-foreground mt-1 font-medium">
            Process multiple manuscripts simultaneously.
          </p>
        </div>
        <div>
          <input
            ref={fileInputRef}
            type="file"
            multiple
            accept=".docx,.pdf,.tex,.md,.txt"
            className="hidden"
            onChange={(e) => handleCreateBatch(e.target.files)}
          />
          <Button
            onClick={() => fileInputRef.current?.click()}
            disabled={uploading}
          >
            {uploading ? (
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
            ) : (
              <Plus className="w-4 h-4 mr-2" />
            )}
            Create Batch
          </Button>
        </div>
      </div>

      {uploadProgress && (
        <Card>
          <CardContent className="py-4">
            <div className="flex items-center gap-3">
              <Loader2 className="w-5 h-5 animate-spin text-primary" />
              <p className="text-sm font-medium">{uploadProgress}</p>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Summary Metrics */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          label="Total Jobs"
          value={jobs.length}
          icon={Layers}
          description="Batch processing jobs"
        />
        <MetricCard
          label="Running"
          value={runningJobs.length}
          icon={Play}
          description="Currently processing"
        />
        <MetricCard
          label="Completed"
          value={completedJobs.length}
          icon={CheckCircle2}
          description="Successfully finished"
        />
        <MetricCard
          label="Total Files"
          value={totalFiles}
          icon={FileText}
          description="Files processed"
        />
      </div>

      {/* Batch Jobs */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">Batch Jobs</CardTitle>
        </CardHeader>
        <CardContent>
          {jobs.length === 0 ? (
            <EmptyState
              icon={Layers}
              title="No batch jobs yet"
              description="Upload multiple files to process them in batch."
              action={{
                label: "Create Batch Job",
                onClick: () => fileInputRef.current?.click(),
              }}
            />
          ) : (
            <div className="space-y-3">
              {jobs.map((job) => (
                <div
                  key={job.id}
                  className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <div className="p-2 bg-muted rounded-lg shrink-0">
                      <Layers className="w-4 h-4 text-muted-foreground" />
                    </div>
                    <div className="min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">
                        {job.batch_name || "Batch Job"}
                      </p>
                      <div className="flex items-center gap-3 mt-1">
                        <span
                          className={`text-xs font-medium px-2 py-0.5 rounded-full ${
                            job.status === "completed"
                              ? "bg-green-100 text-green-700"
                              : job.status === "running"
                              ? "bg-blue-100 text-blue-700"
                              : job.status === "failed"
                              ? "bg-red-100 text-red-700"
                              : "bg-gray-100 text-gray-700"
                          }`}
                        >
                          {job.status}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {job.completed_files}/{job.total_files} files | {job.job_type}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="text-right shrink-0">
                    <div className="w-24 bg-muted rounded-full h-2">
                      <div
                        className="bg-primary h-2 rounded-full transition-all"
                        style={{
                          width: `${
                            job.total_files > 0
                              ? (job.completed_files / job.total_files) * 100
                              : 0
                          }%`,
                        }}
                      />
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      {job.total_files > 0
                        ? Math.round(
                            (job.completed_files / job.total_files) * 100
                          )
                        : 0}
                      %
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-sm">About Batch Processing</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-sm text-muted-foreground">
            Batch processing allows you to upload and process multiple manuscripts
            simultaneously. Each batch job tracks individual file progress, supports
            error recovery, and provides bulk export capabilities. Process up to 100+
            files in a single batch.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
