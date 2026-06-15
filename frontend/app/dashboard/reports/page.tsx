"use client";

import { useState, useEffect } from "react";
import { useSearchParams } from "next/navigation";
import { useAuth } from "@/lib/auth-context";

export default function ReportsPage() {
  const { user } = useAuth();
  const [docId, setDocId] = useState("");
  const [reports, setReports] = useState<any[] | null>(null);
  const searchParams = useSearchParams();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchReports = async (id?: string) => {
    const targetId = id || docId;
    if (!user || !targetId) return;
    setDocId(targetId);
    setLoading(true);
    setError(null);
    try {
      const token = await user.getIdToken();
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"}/api/v1/documents/${targetId}/plagiarism`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      if (!res.ok) {
        const d = await res.json().catch(()=>({}));
        throw new Error(d.detail || "Failed to fetch reports");
      }
      const data = await res.json();
      setReports(data.reports || []);
    } catch (e: any) {
      setError(e.message || String(e));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const q = searchParams.get('docId');
    if (q) {
      fetchReports(q);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams, user]);

  return (
    <div className="max-w-3xl mx-auto py-8">
      <h2 className="text-2xl font-semibold mb-4">Plagiarism Reports</h2>
      <div className="flex gap-2 mb-4">
        <input value={docId} onChange={(e)=>setDocId(e.target.value)} placeholder="Document ID" className="flex-1 border rounded px-3 py-2" />
        <button disabled={!docId || !user || loading} onClick={() => fetchReports()} className="bg-indigo-600 text-white px-4 py-2 rounded">Fetch</button>
      </div>
      {loading && <p>Loading...</p>}
      {error && <p className="text-red-600">{error}</p>}
      {reports && (
        <div className="space-y-4">
          {reports.length === 0 && <p className="text-slate-600">No reports found for this document.</p>}
          {reports.map((r:any)=> (
            <div key={r.id} className="p-4 border rounded">
              <div className="text-sm text-slate-500 mb-2">Report ID: {r.id} — Similarity: {r.similarity_score ?? 0}</div>
              <pre className="whitespace-pre-wrap text-xs">{JSON.stringify(r.report, null, 2)}</pre>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
