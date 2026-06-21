"use client";

import { useState, useEffect, useCallback } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, FileText, ChevronRight, Clock, Loader2 } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { StatusBadge } from "@/components/ui/status-badge";
import { EmptyState } from "@/components/ui/empty-state";
import { LoadingState } from "@/components/ui/loading-state";
import { JournalSelector, Journal } from "@/components/ui/journal-selector";
import { useUpload } from "@/hooks/use-upload";
import { formatFileSize, formatDateShort } from "@/utils/helpers";
import { Document } from "@/types";
import { UploadMode, UploadModeSelector } from "@/components/upload-mode-selector";
import Link from "next/link";

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const { upload, isUploading, error: uploadError, reset: resetUpload } = useUpload();
  const [file, setFile] = useState<File | null>(null);
  const [uploadMode, setUploadMode] = useState<UploadMode | null>(null);
  const [selectedJournal, setSelectedJournal] = useState<Journal | null>(null);
  const [recentDocs, setRecentDocs] = useState<Document[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(true);

  const fetchRecentDocs = useCallback(async () => {
    if (!user) return;
    setLoadingDocs(true);
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"}/api/v1/documents/?limit=5`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        setRecentDocs(data.documents || []);
      }
    } catch {
      console.warn("Failed to fetch recent documents");
    } finally {
      setLoadingDocs(false);
    }
  }, [user]);

  useEffect(() => {
    fetchRecentDocs();
  }, [fetchRecentDocs]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleUpload = async () => {
    if (!file || !user) return;

    try {
      const result = await upload(file, uploadMode || "reconstruction");
      if (selectedJournal) {
        try {
          const token = await user.getIdToken();
          await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"}/api/v1/documents/${result.id}`, {
            method: "PATCH",
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ selected_journal: selectedJournal.id }),
          });
        } catch {
          console.warn("Failed to save journal selection");
        }
      }
      router.push(`/workspace/${result.id}`);
    } catch {
      // Error handled by useUpload
    }
  };

  return (
    <div className="max-w-6xl mx-auto space-y-8 pb-12">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">Research Workspace</h1>
        <p className="text-muted-foreground mt-1 font-medium">Upload your manuscript and prepare it for publication.</p>
      </div>

      {/* Top Area: Upload Mode + File Upload + Journal Selection */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Upload Mode Selection */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Choose Workflow</CardTitle>
              </CardHeader>
              <CardContent>
                <UploadModeSelector
                  selectedMode={uploadMode}
                  onSelect={setUploadMode}
                  disabled={isUploading}
                />
              </CardContent>
            </Card>
          </motion.div>

          {/* Upload Card (shown after mode selection) */}
          {uploadMode && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">
                    {uploadMode === "reconstruction" ? "Upload Raw Manuscript" : "Upload Document for Formatting"}
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <div
                    className={`relative border-2 border-dashed rounded-xl p-8 flex flex-col items-center justify-center transition-all duration-200
                      ${file ? "border-primary bg-primary/5" : "border-border hover:border-primary/50 hover:bg-muted/50"}
                      ${isUploading ? "opacity-50 pointer-events-none" : ""}`}
                  >
                    <input
                      type="file"
                      accept=".docx,.pdf,.tex,.md,.txt"
                      onChange={handleFileChange}
                      disabled={isUploading}
                      className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed z-10"
                      aria-label="Upload manuscript file"
                    />
                    <AnimatePresence mode="wait">
                      {!file ? (
                        <motion.div key="empty" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }} className="flex flex-col items-center pointer-events-none">
                          <div className="p-3 bg-muted rounded-xl mb-3">
                            <UploadCloud className="w-7 h-7 text-primary" />
                          </div>
                          <p className="text-sm font-semibold text-foreground">Drag & drop your manuscript</p>
                          <p className="text-xs text-muted-foreground mt-1">DOCX, PDF, LaTeX, Markdown, or TXT</p>
                        </motion.div>
                      ) : (
                        <motion.div key="file" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex flex-col items-center pointer-events-none">
                          <div className="p-3 bg-primary/10 rounded-xl mb-3">
                            <FileText className="w-7 h-7 text-primary" />
                          </div>
                          <p className="text-sm font-medium text-foreground truncate max-w-[250px]">{file.name}</p>
                          <p className="text-xs text-muted-foreground mt-1">{formatFileSize(file.size)}</p>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>

                  {uploadError && (
                    <p className="text-sm text-destructive mt-3">{uploadError}</p>
                  )}

                  {file && (
                    <div className="mt-4 flex items-center justify-between">
                      <button
                        onClick={() => { setFile(null); resetUpload(); }}
                        className="text-sm text-muted-foreground hover:text-foreground transition-colors"
                      >
                        Choose different file
                      </button>
                      <Button onClick={handleUpload} disabled={isUploading}>
                        {isUploading ? (
                          <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                        ) : (
                          <UploadCloud className="w-4 h-4 mr-2" />
                        )}
                        {uploadMode === "reconstruction" ? "Analyze & Format" : "Format Document"}
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          )}

          {/* Journal Selection */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">Target Journal</CardTitle>
              </CardHeader>
              <CardContent>
                <JournalSelector
                  selectedJournalId={selectedJournal?.id || "ieee"}
                  onSelect={setSelectedJournal}
                  disabled={isUploading}
                />
              </CardContent>
            </Card>
          </motion.div>
        </div>

        {/* Right Column: Recent Documents */}
        <div className="lg:col-span-1">
          <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
            <Card className="sticky top-24">
              <CardHeader className="flex flex-row items-center justify-between">
                <CardTitle className="text-sm">Recent Documents</CardTitle>
                <Link href="/dashboard/documents" className="text-xs text-primary hover:underline">
                  View all
                </Link>
              </CardHeader>
              <CardContent>
                {loadingDocs ? (
                  <LoadingState message="Loading documents..." />
                ) : recentDocs.length === 0 ? (
                  <EmptyState
                    icon={FileText}
                    title="No documents yet"
                    description="Upload your first manuscript to get started."
                  />
                ) : (
                  <div className="space-y-3">
                    {recentDocs.map((doc) => (
                      <Link
                        key={doc.id}
                        href={`/workspace/${doc.id}`}
                        className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-muted/50 transition-colors group"
                      >
                        <div className="flex items-center gap-3 min-w-0">
                          <div className="p-2 bg-muted rounded-lg shrink-0">
                            <FileText className="w-4 h-4 text-muted-foreground" />
                          </div>
                          <div className="min-w-0">
                            <p className="text-sm font-medium text-foreground truncate">{doc.filename}</p>
                            <div className="flex items-center gap-2 mt-0.5">
                              <Clock className="w-3 h-3 text-muted-foreground" />
                              <span className="text-xs text-muted-foreground">{formatDateShort(doc.created_at)}</span>
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
          </motion.div>
        </div>
      </div>
    </div>
  );
}
