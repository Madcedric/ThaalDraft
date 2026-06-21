'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import {
  ArrowLeft, RefreshCw, Activity, Loader2,
  AlertCircle, CheckCircle2, BookOpen, Zap, Settings
} from 'lucide-react';
import { getDocument, updateDocument, getCitationHealth, analyzeReview, getReviewReport } from '@/services/api';
import { useDocumentSync } from '@/hooks/useDocumentSync';
import { StructurePane } from '@/components/workspace/StructurePane';
import { ManuscriptPane } from '@/components/workspace/ManuscriptPane';
import { AnalysisPane } from '@/components/workspace/AnalysisPane';
import type { Document, StructuredData } from '@/types';

// ── Types ─────────────────────────────────────────────────────────────────────

interface Section {
  id: string;
  title: string;
  level: number;
  content: string;
}

type WorkspaceMode = 'reconstruction' | 'formatting';

// ── Auth helper ───────────────────────────────────────────────────────────────

function getToken(): string | null {
  if (typeof window === 'undefined') return null;
  try {
    const raw = localStorage.getItem('firebase_id_token') || sessionStorage.getItem('firebase_id_token');
    return raw;
  } catch {
    return null;
  }
}

// ── Workspace Page ─────────────────────────────────────────────────────────────

export default function WorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const documentId = params?.id as string;

  const [doc, setDoc] = useState<Document | null>(null);
  const [sections, setSections] = useState<Section[]>([]);
  const [activeSection, setActiveSection] = useState<string>('');
  const [content, setContent] = useState<string>('');
  const [mode, setMode] = useState<WorkspaceMode>('reconstruction');
  const [healthScore, setHealthScore] = useState<number>(0);
  const [citationsCount, setCitationsCount] = useState<number>(0);
  const [issuesCount, setIssuesCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [processingStatus, setProcessingStatus] = useState<string | null>(null);
  const [isReconstructing, setIsReconstructing] = useState(false);

  // WebSocket connection for real-time updates
  const { latestUpdate, connectionStatus } = useDocumentSync(documentId);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  // ── Load Document ──────────────────────────────────────────────────────────

  const loadDocument = useCallback(async () => {
    const token = getToken();
    if (!token || !documentId) { setError('Not authenticated'); setIsLoading(false); return; }

    try {
      const data = await getDocument(documentId, token);
      setDoc(data);

      // Build sections from parsed_json
      const parsed = data.parsed_json as StructuredData | undefined;
      if (parsed?.sections) {
        const secs = parsed.sections.map((s, i) => ({
          id: `section-${i}`,
          title: s.heading || `Section ${i + 1}`,
          level: s.level ?? 1,
          content: s.content,
        }));
        setSections(secs);
        if (secs.length > 0) {
          setActiveSection(secs[0].id);
          setContent(secs[0].content);
        }
      } else if (parsed?.abstract) {
        setContent(parsed.abstract as string);
      }

      // Load citation health
      try {
        const health = await getCitationHealth(documentId, token);
        setHealthScore(Math.round(health.health_score?.overall ?? 0));
        setCitationsCount(health.total_references ?? 0);
      } catch {
        /* citation data not yet available */
      }

    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load document');
    } finally {
      setIsLoading(false);
    }
  }, [documentId]);

  useEffect(() => { loadDocument(); }, [loadDocument]);

  // ── React to WebSocket updates ─────────────────────────────────────────────

  useEffect(() => {
    if (!latestUpdate) return;
    const { event } = latestUpdate;
    if (event === 'job_completed') {
      setProcessingStatus('Processing complete. Refreshing...');
      setTimeout(() => { loadDocument(); setProcessingStatus(null); }, 1500);
    } else if (event === 'job_failed') {
      setProcessingStatus('Processing encountered an error.');
    }
  }, [latestUpdate, loadDocument]);

  // ── Section Navigation ─────────────────────────────────────────────────────

  const handleSectionClick = (id: string) => {
    // Save current section before switching
    setSections(prev => prev.map(s => s.id === activeSection ? { ...s, content } : s));
    const target = sections.find(s => s.id === id);
    if (target) { setActiveSection(id); setContent(target.content); }
  };

  // ── Reconstruction Pipeline ────────────────────────────────────────────────

  const handleReconstruct = async () => {
    const token = getToken();
    if (!token || !documentId) return;
    setIsReconstructing(true);
    try {
      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'}/api/v1/documents/${documentId}/reconstruct`,
        {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        }
      );
      if (!response.ok) throw new Error('Reconstruction failed');
      // Reload document after reconstruction
      await loadDocument();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Reconstruction failed');
    } finally {
      setIsReconstructing(false);
    }
  };

  // ── Auto-save on content change ────────────────────────────────────────────

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    setSections(prev => prev.map(s => s.id === activeSection ? { ...s, content: newContent } : s));

    if (saveTimer.current) clearTimeout(saveTimer.current);
    setIsSaving(true);

    saveTimer.current = setTimeout(async () => {
      const token = getToken();
      if (!token || !documentId) { setIsSaving(false); return; }
      try {
        // Persist the updated content to the backend
        const updatedSections = sections.map(s => s.id === activeSection ? { ...s, content: newContent } : s);
        const currentParsedJson = (doc?.parsed_json ?? {}) as Record<string, unknown>;
        await updateDocument(documentId, {
          parsed_json: {
            ...currentParsedJson,
            sections: updatedSections.map(s => ({
              heading: s.title,
              content: s.content,
              level: s.level,
            })),
          }
        }, token);
      } catch {
        /* silently fail auto-save */
      }
      setIsSaving(false);
    }, 1500);
  };

  // ── Render States ──────────────────────────────────────────────────────────

  if (isLoading) {
    return (
      <div className="h-screen bg-zinc-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 text-blue-400 animate-spin" />
          <p className="text-zinc-400 text-sm">Loading workspace...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen bg-zinc-950 flex items-center justify-center">
        <div className="flex flex-col items-center gap-3 text-center max-w-sm">
          <AlertCircle className="w-10 h-10 text-rose-400" />
          <h2 className="text-zinc-200 font-semibold">Failed to load workspace</h2>
          <p className="text-zinc-500 text-sm">{error}</p>
          <Link href="/dashboard" className="mt-2 text-blue-400 hover:text-blue-300 text-sm underline underline-offset-4">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const isProcessing = doc?.status === 'uploaded' || doc?.status === 'parsing';

  return (
    <div className="h-screen bg-zinc-950 flex flex-col overflow-hidden font-sans">
      {/* ── Top Navigation Bar ──────────────────────────────────────────── */}
      <header className="h-12 bg-zinc-900 border-b border-zinc-800 flex items-center px-4 gap-3 shrink-0 z-20">
        <Link
          href="/dashboard"
          className="flex items-center gap-1.5 text-zinc-400 hover:text-zinc-200 transition-colors text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="hidden sm:inline">Dashboard</span>
        </Link>

        <div className="h-4 border-l border-zinc-800 mx-1" />

        <h1 className="text-sm font-medium text-zinc-300 truncate flex-1">
          {doc?.filename ?? 'Untitled'}
        </h1>

        <div className="flex items-center gap-2 ml-auto">
          {/* Processing status badge */}
          {isProcessing && (
            <span className="flex items-center gap-1.5 text-xs font-medium text-amber-400 bg-amber-400/10 border border-amber-400/20 px-2.5 py-1 rounded-full">
              <RefreshCw className="w-3 h-3 animate-spin" />
              Processing...
            </span>
          )}
          {processingStatus && !isProcessing && (
            <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-400 bg-emerald-400/10 border border-emerald-400/20 px-2.5 py-1 rounded-full">
              <CheckCircle2 className="w-3 h-3" />
              {processingStatus}
            </span>
          )}

          {/* WS connection indicator */}
          <span className={`w-2 h-2 rounded-full ${connectionStatus === 'Open' ? 'bg-emerald-400' : 'bg-zinc-600'}`}
            title={`WebSocket: ${connectionStatus}`} />

          {/* Document Status Badge */}
          <span className="text-xs text-zinc-500 capitalize bg-zinc-800 px-2 py-1 rounded-md border border-zinc-700">
            {doc?.status ?? '–'}
          </span>
        </div>
      </header>

      {/* ── Processing Banner ───────────────────────────────────────────── */}
      {isProcessing && (
        <div className="bg-blue-500/10 border-b border-blue-500/20 px-4 py-2.5 flex items-center gap-2.5 text-sm">
          <Zap className="w-4 h-4 text-blue-400 shrink-0" />
          <span className="text-blue-300">
            Your document is being processed in the background. The workspace will update automatically when complete.
          </span>
        </div>
      )}

      {/* ── 3-Pane Layout ───────────────────────────────────────────────── */}
      <div className="flex flex-1 overflow-hidden">
        {/* Pane 1: Structure */}
        <StructurePane
          sections={sections}
          activeSection={activeSection}
          onSectionClick={handleSectionClick}
        />

        {/* Pane 2: Live Manuscript */}
        <ManuscriptPane
          content={content}
          onChange={handleContentChange}
          isSaving={isSaving}
          title={doc?.filename?.replace(/\.[^.]+$/, '') ?? 'Manuscript'}
        />

        {/* Pane 3: Analysis */}
        <AnalysisPane
          healthScore={healthScore}
          citationsCount={citationsCount}
          issuesCount={issuesCount}
          mode={mode}
          onModeChange={setMode}
          documentId={documentId}
          onReconstruct={handleReconstruct}
          isReconstructing={isReconstructing}
        />
      </div>
    </div>
  );
}
