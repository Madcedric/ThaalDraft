"use client";

import { useState, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { uploadDocument, UploadDocumentResponse } from "@/services/api";

interface UseUploadReturn {
  upload: (file: File, mode?: string) => Promise<UploadDocumentResponse>;
  isUploading: boolean;
  error: string | null;
  reset: () => void;
}

export function useUpload(): UseUploadReturn {
  const { user } = useAuth();
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const upload = useCallback(
    async (file: File, mode: string = "reconstruction"): Promise<UploadDocumentResponse> => {
      if (!user) {
        throw new Error("User not authenticated");
      }

      setIsUploading(true);
      setError(null);

      try {
        const token = await user.getIdToken();
        const result = await uploadDocument(file, token, mode);
        return result;
      } catch (err) {
        const message = err instanceof Error ? err.message : "Upload failed";
        setError(message);
        throw err;
      } finally {
        setIsUploading(false);
      }
    },
    [user]
  );

  const reset = useCallback(() => {
    setError(null);
    setIsUploading(false);
  }, []);

  return { upload, isUploading, error, reset };
}
