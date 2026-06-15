"use client";

import { useEffect, useState, useCallback } from "react";
import { useAuth } from "@/lib/auth-context";
import { useParams } from "next/navigation";

interface DocumentData {
  id: string;
  filename: string;
  status: string;
  storage_path: string;
  parsed_json: Record<string, unknown> | null;
  ai_classification: Record<string, unknown> | null;
  structured_json: Record<string, unknown> | null;
}

interface JobData {
  id: string;
  type: string;
  status: string;
  created_at: string;
  result: unknown;
}

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function DocumentPage() {
  const { user } = useAuth();
  const params = useParams();
  const id = params?.id as string;
  const [doc, setDoc] = useState<DocumentData | null>(null);
  const [jobs, setJobs] = useState<JobData[] | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [enqueueing, setEnqueueing] = useState(false);

  const fetchJobs = useCallback(async () => {
    if (!user || !id) return;
    try {
      const token = await user.getIdToken();
      const res = await fetch(`${API_BASE}/api/v1/documents/${id}/jobs`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) throw new Error("Failed to fetch jobs");
      const data = await res.json();
      setJobs(data.jobs || []);
    } catch (e: unknown) {
      console.warn(e);
    }
  }, [user, id]);

  useEffect(() => {
    const fetchDoc = async () => {
      if (!user || !id) return;
      setLoading(true);
      try {
        const token = await user.getIdToken();
        const res = await fetch(`${API_BASE}/api/v1/documents/${id}`, {
          headers: { Authorization: `Bearer ${token}` }
        });
        if (!res.ok) throw new Error("Failed to fetch document");
        const data = await res.json();
        setDoc(data);
        fetchJobs();
      } catch (e: unknown) {
        const message = e instanceof Error ? e.message : String(e);
        setError(message);
      } finally {
        setLoading(false);
      }
    };
    fetchDoc();
  }, [user, id, fetchJobs]);

  // Poll jobs every 5 seconds
  useEffect(() => {
    const iv = setInterval(() => {
      fetchJobs();
    }, 5000);
    return () => clearInterval(iv);
  }, [fetchJobs]);

  const enqueuePlagiarism = async () => {
    if (!user || !id) return;
    setEnqueueing(true);
    try {
      const token = await user.getIdToken();
      const res = await fetch(`${API_BASE}/api/v1/documents/${id}/jobs`, {
        method: "POST",
        headers: { "Content-Type": "application/json", Authorization: `Bearer ${token}` },
        body: JSON.stringify({ type: "plagiarism" })
      });
      if (!res.ok) throw new Error("Failed to enqueue job");
      const j = await res.json();
      alert(`Enqueued job ${j.id || j.document_id || 'ok'}`);
    } catch (e: unknown) {
      const message = e instanceof Error ? e.message : String(e);
      setError(message);
    } finally {
      setEnqueueing(false);
    }
  };

  if (loading) return <div className="p-8">Loading...</div>;
  if (error) return <div className="p-8 text-red-600">{error}</div>;
  if (!doc) return <div className="p-8">No document loaded.</div>;

  return (
    <div className="max-w-4xl mx-auto p-8 space-y-6">
      <h2 className="text-2xl font-semibold">Document: {doc.id}</h2>
      <div className="p-4 border rounded">
        <div><strong>Filename:</strong> {doc.filename}</div>
        <div><strong>Status:</strong> {doc.status}</div>
        <div><strong>Storage:</strong> {doc.storage_path}</div>
      </div>

      <div className="p-4 border rounded">
        <h3 className="font-semibold mb-2">Jobs</h3>
        {!jobs && <div className="text-sm text-slate-500">Loading jobs...</div>}
        {jobs && jobs.length === 0 && <div className="text-sm text-slate-500">No jobs yet.</div>}
        {jobs && jobs.length > 0 && (
          <ul className="space-y-2 text-sm">
            {jobs.map(j => (
              <li key={j.id} className="border p-2 rounded flex justify-between items-center">
                <div>
                  <div className="font-medium">{j.type}</div>
                  <div className="text-xs text-slate-500">{j.status} — {j.created_at}</div>
                </div>
                <div className="text-xs text-slate-400">{j.result ? 'Result' : ''}</div>
              </li>
            ))}
          </ul>
        )}
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="p-4 border rounded">
          <h4 className="font-semibold mb-2">Parsed JSON</h4>
          <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(doc.parsed_json || {}, null, 2)}</pre>
        </div>
        <div className="p-4 border rounded">
          <h4 className="font-semibold mb-2">AI Classification / Structured</h4>
          <pre className="text-xs whitespace-pre-wrap">{JSON.stringify(doc.ai_classification || doc.structured_json || {}, null, 2)}</pre>
        </div>
      </div>

      <div className="space-y-2">
        <button disabled={enqueueing} onClick={enqueuePlagiarism} className="bg-indigo-600 text-white px-4 py-2 rounded">Enqueue Plagiarism Check</button>
      </div>
    </div>
  );
}
