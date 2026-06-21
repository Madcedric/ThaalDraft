'use client';

import { useState, useEffect, useCallback, useRef } from 'react';
import { useParams, useRouter } from 'next/navigation';
import Link from 'next/link';
import Image from 'next/image';
import {
  ArrowLeft, RefreshCw, Loader2,
  AlertCircle, CheckCircle2, Zap, XCircle, Circle
} from 'lucide-react';
import { getDocument, updateDocument, getCitationHealth } from '@/services/api';
import { useDocumentSync } from '@/hooks/useDocumentSync';
import { useAuth } from '@/lib/auth-context';
import { StructurePane } from '@/components/workspace/StructurePane';
import { ManuscriptPane } from '@/components/workspace/ManuscriptPane';
import { AnalysisPane } from '@/components/workspace/AnalysisPane';
import type { Document, StructuredData } from '@/types';

interface Section {
  id: string;
  title: string;
  level: number;
  content: string;
}

type WorkspaceMode = 'reconstruction' | 'formatting';

const STEP_LABELS: Record<string, string> = {
  parse: 'Parse & Extract',
  structure: 'Build Structure',
  citations: 'Citation Analysis',
  compliance: 'Compliance Check',
  review: 'AI Review',
};

const STEP_ORDER = ['parse', 'structure', 'citations', 'compliance', 'review'];

export default function WorkspacePage() {
  const params = useParams();
  const router = useRouter();
  const { user } = useAuth();
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

  const {
    latestUpdate,
    connectionStatus,
    reconstructionSteps,
    reconstructionProgress,
    isReconstructing: wsReconstructing,
  } = useDocumentSync(documentId);
  const saveTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const loadDocument = useCallback(async () => {
    if (!user || !documentId) { setError('Not authenticated'); setIsLoading(false); return; }
    const token = await user.getIdToken();

    try {
      const data = await getDocument(documentId, token);
      setDoc(data);

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
  }, [documentId, user]);

  useEffect(() => { loadDocument(); }, [loadDocument]);

  useEffect(() => {
    if (!latestUpdate) return;
    const { event } = latestUpdate;
    if (event === 'job_completed') {
      setProcessingStatus('Processing complete. Refreshing...');
      setIsReconstructing(false);
      setTimeout(() => { loadDocument(); setProcessingStatus(null); }, 1500);
    } else if (event === 'job_failed') {
      setProcessingStatus('Processing encountered an error.');
      setIsReconstructing(false);
    }
  }, [latestUpdate, loadDocument]);

  useEffect(() => {
    if (wsReconstructing) setIsReconstructing(true);
  }, [wsReconstructing]);

  const handleSectionClick = (id: string) => {
    setSections(prev => prev.map(s => s.id === activeSection ? { ...s, content } : s));
    const target = sections.find(s => s.id === id);
    if (target) { setActiveSection(id); setContent(target.content); }
  };

  const handleReconstruct = async () => {
    if (!user || !documentId) return;
    const token = await user.getIdToken();
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
      await loadDocument();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Reconstruction failed');
      setIsReconstructing(false);
    }
  };

  const handleContentChange = (newContent: string) => {
    setContent(newContent);
    setSections(prev => prev.map(s => s.id === activeSection ? { ...s, content: newContent } : s));

    if (saveTimer.current) clearTimeout(saveTimer.current);
    setIsSaving(true);

    saveTimer.current = setTimeout(async () => {
      if (!user || !documentId) { setIsSaving(false); return; }
      const token = await user.getIdToken();
      try {
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

  if (isLoading) {
    return (
      <div className="h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-3">
          <Loader2 className="w-8 h-8 text-[#D4AF37] animate-spin" />
          <p className="text-muted-foreground text-sm">Loading workspace...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="h-screen bg-background flex items-center justify-center">
        <div className="flex flex-col items-center gap-3 text-center max-w-sm">
          <AlertCircle className="w-10 h-10 text-destructive" />
          <h2 className="text-foreground font-semibold">Failed to load workspace</h2>
          <p className="text-muted-foreground text-sm">{error}</p>
          <Link href="/dashboard" className="mt-2 text-[#D4AF37] hover:text-[#D4AF37]/80 text-sm underline underline-offset-4">
            Back to Dashboard
          </Link>
        </div>
      </div>
    );
  }

  const isProcessing = doc?.status === 'uploaded' || doc?.status === 'parsing' || isReconstructing;

  return (
    <div className="h-screen bg-background flex flex-col overflow-hidden font-sans">
      {/* Top Navigation Bar */}
      <header className="h-12 bg-card border-b border-border flex items-center px-4 gap-3 shrink-0 z-20">
        <Link
          href="/dashboard"
          className="flex items-center gap-1.5 text-muted-foreground hover:text-foreground transition-colors text-sm"
        >
          <ArrowLeft className="w-4 h-4" />
          <span className="hidden sm:inline">Dashboard</span>
        </Link>

        <div className="h-4 border-l border-border mx-1" />

        <div className="flex items-center gap-2">
          <Image src="/titleIcon.png" alt="ThaalDraft" width={24} height={24} className="rounded-md" />
          <h1 className="text-sm font-medium text-foreground truncate max-w-[200px] md:max-w-none">
            {doc?.filename ?? 'Untitled'}
          </h1>
        </div>

        <div className="flex items-center gap-2 ml-auto">
          {isReconstructing && (
            <span className="flex items-center gap-1.5 text-xs font-medium text-[#D4AF37] bg-[#D4AF37]/10 border border-[#D4AF37]/20 px-2.5 py-1 rounded-full">
              <RefreshCw className="w-3 h-3 animate-spin" />
              Reconstructing... {reconstructionProgress}%
            </span>
          )}
          {processingStatus && !isReconstructing && (
            <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-600 bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-full">
              <CheckCircle2 className="w-3 h-3" />
              {processingStatus}
            </span>
          )}

          <span className={`w-2 h-2 rounded-full ${connectionStatus === 'Open' ? 'bg-emerald-500' : 'bg-muted-foreground/40'}`}
            title={`WebSocket: ${connectionStatus}`} />

          <span className="text-xs text-muted-foreground capitalize bg-muted px-2.5 py-1 rounded-full border border-border font-medium">
            {doc?.status ?? '–'}
          </span>
        </div>
      </header>

      {/* Reconstruction Progress Bar */}
      {isReconstructing && reconstructionSteps.length > 0 && (
        <div className="bg-card border-b border-border px-4 py-3 shrink-0">
          <div className="flex items-center justify-between mb-2">
            <span className="text-xs font-semibold text-foreground">Reconstruction Pipeline</span>
            <span className="text-xs font-medium text-[#D4AF37]">{reconstructionProgress}%</span>
          </div>
          <div className="w-full bg-border rounded-full h-1.5 mb-3">
            <div
              className="h-1.5 rounded-full bg-[#D4AF37] transition-all duration-500"
              style={{ width: `${reconstructionProgress}%` }}
            />
          </div>
          <div className="flex gap-1.5">
            {STEP_ORDER.map((stepKey) => {
              const step = reconstructionSteps.find(s => s.step === stepKey);
              const status = step?.status;
              const Icon = status === 'completed' ? CheckCircle2
                : status === 'failed' ? XCircle
                : status === 'running' ? Loader2
                : Circle;
              const color = status === 'completed' ? 'text-emerald-500'
                : status === 'failed' ? 'text-red-500'
                : status === 'running' ? 'text-[#D4AF37]'
                : 'text-muted-foreground/40';

              return (
                <div key={stepKey} className="flex items-center gap-1.5 text-xs">
                  <Icon className={`w-3.5 h-3.5 ${color} ${status === 'running' ? 'animate-spin' : ''}`} />
                  <span className={`hidden sm:inline ${status === 'completed' ? 'text-foreground' : status === 'running' ? 'text-[#D4AF37] font-medium' : 'text-muted-foreground'}`}>
                    {STEP_LABELS[stepKey]}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      )}

      {/* Processing Banner (before reconstruction starts) */}
      {isProcessing && !isReconstructing && reconstructionSteps.length === 0 && (
        <div className="bg-[#D4AF37]/5 border-b border-[#D4AF37]/10 px-4 py-2.5 flex items-center gap-2.5 text-sm">
          <Zap className="w-4 h-4 text-[#D4AF37] shrink-0" />
          <span className="text-muted-foreground">
            Your document is being processed in the background. The workspace will update automatically when complete.
          </span>
        </div>
      )}

      {/* 3-Pane Layout */}
      <div className="flex flex-1 overflow-hidden">
        <StructurePane
          sections={sections}
          activeSection={activeSection}
          onSectionClick={handleSectionClick}
        />

        <ManuscriptPane
          content={content}
          onChange={handleContentChange}
          isSaving={isSaving}
          title={doc?.filename?.replace(/\.[^.]+$/, '') ?? 'Manuscript'}
        />

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
