"use client";

import { useState, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { getPlagiarismReports } from "@/services/api";
import { PlagiarismCheck } from "@/types";

interface UsePlagiarismReturn {
  reports: PlagiarismCheck[];
  loading: boolean;
  error: string | null;
  fetchReports: (documentId: string) => Promise<void>;
}

export function usePlagiarism(): UsePlagiarismReturn {
  const { user } = useAuth();
  const [reports, setReports] = useState<PlagiarismCheck[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = useCallback(
    async (documentId: string) => {
      if (!user) return;

      setLoading(true);
      setError(null);

      try {
        const token = await user.getIdToken();
        const data = await getPlagiarismReports(documentId, token);
        setReports(data.reports || []);
      } catch (err) {
        const message = err instanceof Error ? err.message : "Failed to fetch reports";
        setError(message);
      } finally {
        setLoading(false);
      }
    },
    [user]
  );

  return { reports, loading, error, fetchReports };
}
