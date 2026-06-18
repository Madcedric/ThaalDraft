"use client";

import { useState, useEffect, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { MetricCard } from "@/components/ui/metric-card";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { ErrorState } from "@/components/ui/error-state";
import { BatchJob } from "@/types";
import {
  Layers,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Clock,
  Play,
  Plus,
} from "lucide-react";

export default function BatchPage() {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<BatchJob[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchJobs = useCallback(async () => {
    if (!user) return;
    setLoading(true);
    setError(null);
    try {
      const token = await user.getIdToken();
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"}/api/v1/batch/jobs`,
        { headers: { Authorization: `Bearer ${token}` } }
      );
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

  const runningJobs = jobs.filter((j) => j.status === "running");
  const completedJobs = jobs.filter((j) => j.status === "completed");
  const failedJobs = jobs.filter((j) => j.status === "failed");
  const totalFiles = jobs.reduce((sum, j) => sum + j.total_files, 0);

  if (loading) return <LoadingState message="Loading batch data..." />;
  if (error) return <ErrorState message={error} onRetry={fetchJobs} />;

  return (
    <div className="max-w-5xl mx-auto space-y-6 pb-12">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">
          Batch Processing
        </h1>
        <p className="text-muted-foreground mt-1 font-medium">
          Process multiple manuscripts simultaneously.
        </p>
      </div>

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
          <div className="flex items-center justify-between">
            <CardTitle className="text-sm">Batch Jobs</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          {jobs.length === 0 ? (
            <EmptyState
              icon={Layers}
              title="No batch jobs yet"
              description="Upload multiple files to process them in batch."
              action={{
                label: "Create Batch Job",
                onClick: () => (window.location.href = "/dashboard"),
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
                        Batch Job
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
