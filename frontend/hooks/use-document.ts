"use client";

import { useState, useEffect, useCallback, useRef } from "react";
import { useAuth } from "@/lib/auth-context";
import { getDocument, getDocumentJobs } from "@/services/api";
import { Document, Job } from "@/types";

interface UseDocumentReturn {
  document: Document | null;
  jobs: Job[];
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
  refreshJobs: () => Promise<void>;
}

export function useDocument(documentId: string | null): UseDocumentReturn {
  const { user } = useAuth();
  const [document, setDocument] = useState<Document | null>(null);
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fetchedRef = useRef(false);

  const fetchDocument = useCallback(async () => {
    if (!user || !documentId) return;

    setLoading(true);
    setError(null);

    try {
      const token = await user.getIdToken();
      const doc = await getDocument(documentId, token);
      setDocument(doc);
    } catch (err) {
      const message = err instanceof Error ? err.message : "Failed to fetch document";
      setError(message);
    } finally {
      setLoading(false);
    }
  }, [user, documentId]);

  const fetchJobs = useCallback(async () => {
    if (!user || !documentId) return;

    try {
      const token = await user.getIdToken();
      const data = await getDocumentJobs(documentId, token);
      setJobs(data.jobs || []);
    } catch (err) {
      console.warn("Failed to fetch jobs:", err);
    }
  }, [user, documentId]);

  useEffect(() => {
    if (fetchedRef.current) return;
    fetchedRef.current = true;
    fetchDocument();
    fetchJobs();
  }, [fetchDocument, fetchJobs]);

  useEffect(() => {
    if (!documentId) return;

    const interval = setInterval(() => {
      fetchJobs();
    }, 5000);

    return () => clearInterval(interval);
  }, [documentId, fetchJobs]);

  return {
    document,
    jobs,
    loading,
    error,
    refresh: fetchDocument,
    refreshJobs: fetchJobs,
  };
}
