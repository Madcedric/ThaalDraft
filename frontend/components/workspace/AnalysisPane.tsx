'use client';

import React, { useState } from 'react';
import { Activity, BookOpen, AlertCircle, CheckCircle2, Download, FileText, Loader2, Send, Package } from 'lucide-react';
import { useAuth } from '@/lib/auth-context';

interface AnalysisPaneProps {
  healthScore: number;
  citationsCount: number;
  issuesCount: number;
  mode: 'reconstruction' | 'formatting';
  onModeChange: (mode: 'reconstruction' | 'formatting') => void;
  documentId?: string;
  onReconstruct?: () => void;
  isReconstructing?: boolean;
}

const TEMPLATES = [
  { id: 'ieee', name: 'IEEE', desc: 'Two-column conference' },
  { id: 'acm', name: 'ACM', desc: 'CS conference proceedings' },
  { id: 'springer', name: 'Springer LNCS', desc: 'Lecture Notes in CS' },
  { id: 'elsevier', name: 'Elsevier', desc: 'Scientific journal' },
  { id: 'apa', name: 'APA 7th', desc: 'Psychology standard' },
  { id: 'mla', name: 'MLA 9th', desc: 'Humanities format' },
  { id: 'nature', name: 'Nature', desc: 'Scientific journal' },
];

const EXPORT_FORMATS = [
  { id: 'docx', label: 'DOCX', ext: '.docx' },
  { id: 'latex', label: 'LaTeX', ext: '.tex' },
  { id: 'zip', label: 'ZIP Package', ext: '.zip' },
];

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000';

export function AnalysisPane({
  healthScore,
  citationsCount,
  issuesCount,
  mode,
  onModeChange,
  documentId,
  onReconstruct,
  isReconstructing = false,
}: AnalysisPaneProps) {
  const { user } = useAuth();
  const [selectedTemplate, setSelectedTemplate] = useState('ieee');
  const [isExporting, setIsExporting] = useState(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);
  const [isBuildingSubmission, setIsBuildingSubmission] = useState(false);
  const [submissionBuilt, setSubmissionBuilt] = useState(false);

  const handleExport = async (format: string) => {
    if (!documentId || !user) return;
    setIsExporting(true);
    setExportMessage(null);
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${API_BASE}/api/v1/documents/${documentId}/export`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ template: selectedTemplate, format }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Export failed');
      }

      const blob = await response.blob();
      const disposition = response.headers.get('Content-Disposition') || '';
      const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
      const filename = filenameMatch ? filenameMatch[1] : `manuscript_${selectedTemplate}.${format === 'zip' ? 'zip' : format === 'latex' ? 'tex' : 'docx'}`;

      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      a.click();
      URL.revokeObjectURL(url);

      setExportMessage(`Exported as ${filename}`);
    } catch (err: unknown) {
      setExportMessage(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setIsExporting(false);
    }
  };

  const handleBuildSubmission = async () => {
    if (!documentId || !user) return;
    setIsBuildingSubmission(true);
    setExportMessage(null);
    try {
      const token = await user.getIdToken();
      const response = await fetch(`${API_BASE}/api/v1/documents/${documentId}/submission/build`, {
        method: 'POST',
        headers: { Authorization: `Bearer ${token}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({
          journal_id: selectedTemplate,
          template_id: selectedTemplate,
          components: ['manuscript_docx', 'compliance_report', 'review_report', 'citation_report', 'cover_letter', 'author_statement', 'conflict_statement'],
        }),
      });

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || 'Build failed');
      }

      setSubmissionBuilt(true);
      setExportMessage('Submission package built!');

      const zipResponse = await fetch(`${API_BASE}/api/v1/documents/${documentId}/submission/download-zip`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (zipResponse.ok) {
        const blob = await zipResponse.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${documentId}_submission.zip`;
        a.click();
        URL.revokeObjectURL(url);
      }
    } catch (err: unknown) {
      setExportMessage(err instanceof Error ? err.message : 'Build failed');
    } finally {
      setIsBuildingSubmission(false);
    }
  };

  return (
    <div className="w-72 h-full bg-card border-l border-border flex flex-col hidden lg:flex">
      {/* Mode Selector */}
      <div className="p-4 border-b border-border">
        <div className="bg-muted p-1 rounded-lg flex text-xs font-medium border border-border">
          <button
            onClick={() => onModeChange('reconstruction')}
            className={`flex-1 py-2 px-2 rounded-md transition-all duration-200 ${
              mode === 'reconstruction'
                ? 'bg-[#0F1B33] text-white shadow-sm'
                : 'text-muted-foreground hover:text-foreground hover:bg-background'
            }`}
          >
            Reconstruct
          </button>
          <button
            onClick={() => onModeChange('formatting')}
            className={`flex-1 py-2 px-2 rounded-md transition-all duration-200 ${
              mode === 'formatting'
                ? 'bg-[#D4AF37] text-[#0F1B33] shadow-sm font-semibold'
                : 'text-muted-foreground hover:text-foreground hover:bg-background'
            }`}
          >
            Format Studio
          </button>
        </div>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {/* Reconstruction Mode */}
        {mode === 'reconstruction' && (
          <>
            {/* Reconstruct Button */}
            <button
              onClick={onReconstruct}
              disabled={isReconstructing}
              className="w-full py-2.5 px-3 bg-[#0F1B33] hover:bg-[#1D2C4D] disabled:bg-muted disabled:text-muted-foreground text-white text-sm font-medium rounded-lg transition-all duration-200 flex items-center justify-center gap-2 shadow-sm hover:shadow-md"
            >
              {isReconstructing ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Reconstructing...
                </>
              ) : (
                <>
                  <Activity className="w-4 h-4" />
                  Run Full Reconstruction
                </>
              )}
            </button>

            {/* Health Score */}
            <div className="bg-muted/50 border border-border rounded-lg p-4 hover:border-[#D4AF37]/20 transition-colors">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center">
                  <Activity className="w-3.5 h-3.5 mr-1.5" />
                  Document Health
                </h3>
                <span className={`text-sm font-bold ${healthScore >= 80 ? 'text-emerald-600' : healthScore >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
                  {healthScore}/100
                </span>
              </div>
              <div className="w-full bg-border rounded-full h-2">
                <div
                  className={`h-2 rounded-full transition-all duration-500 ${healthScore >= 80 ? 'bg-emerald-500' : healthScore >= 50 ? 'bg-amber-500' : 'bg-red-500'}`}
                  style={{ width: `${healthScore}%` }}
                />
              </div>
            </div>

            {/* Citations */}
            <div className="bg-muted/50 border border-border rounded-lg p-4 hover:border-[#D4AF37]/20 transition-colors">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center mb-3">
                <BookOpen className="w-3.5 h-3.5 mr-1.5" />
                Citations
              </h3>
              <div className="flex items-end justify-between">
                <div>
                  <div className="text-2xl font-semibold text-foreground">{citationsCount}</div>
                  <div className="text-xs text-muted-foreground mt-0.5">Total References</div>
                </div>
                {issuesCount > 0 ? (
                  <div className="flex items-center text-xs font-medium text-red-600 bg-red-50 border border-red-200 px-2 py-1 rounded-full">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    {issuesCount} Issues
                  </div>
                ) : (
                  <div className="flex items-center text-xs font-medium text-emerald-600 bg-emerald-50 border border-emerald-200 px-2 py-1 rounded-full">
                    <CheckCircle2 className="w-3 h-3 mr-1" />
                    All Valid
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {/* Formatting Mode */}
        {mode === 'formatting' && (
          <>
            {/* Template Picker */}
            <div className="bg-muted/50 border border-border rounded-lg p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center mb-3">
                <FileText className="w-3.5 h-3.5 mr-1.5" />
                Journal Template
              </h3>
              <div className="space-y-1.5">
                {TEMPLATES.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setSelectedTemplate(t.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-200 ${
                      selectedTemplate === t.id
                        ? 'bg-[#D4AF37]/10 border border-[#D4AF37]/30 text-[#0F1B33] font-medium shadow-sm'
                        : 'bg-background border border-border text-muted-foreground hover:bg-muted hover:text-foreground hover:border-[#D4AF37]/20'
                    }`}
                  >
                    <div className="font-medium">{t.name}</div>
                    <div className="text-xs opacity-60">{t.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Export Buttons */}
            <div className="bg-muted/50 border border-border rounded-lg p-4">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground flex items-center mb-3">
                <Download className="w-3.5 h-3.5 mr-1.5" />
                Export
              </h3>
              <div className="space-y-2">
                {EXPORT_FORMATS.map((f) => (
                  <button
                    key={f.id}
                    onClick={() => handleExport(f.id)}
                    disabled={isExporting || !documentId}
                    className="w-full py-2.5 px-3 bg-card hover:bg-muted disabled:bg-muted disabled:text-muted-foreground text-foreground text-sm font-medium rounded-lg transition-all duration-200 flex items-center justify-center gap-2 border border-border hover:border-[#D4AF37]/30 hover:shadow-sm"
                  >
                    {isExporting ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Download className="w-4 h-4" />
                    )}
                    {f.label} <span className="text-muted-foreground text-xs">{f.ext}</span>
                  </button>
                ))}
              </div>
              {exportMessage && (
                <p className={`text-xs mt-2 text-center ${exportMessage.includes('failed') ? 'text-red-600' : 'text-emerald-600'}`}>
                  {exportMessage}
                </p>
              )}
            </div>

            {/* Submit to Journal */}
            <button
              onClick={handleBuildSubmission}
              disabled={!documentId || isBuildingSubmission}
              className="w-full py-2.5 px-3 bg-[#D4AF37] hover:bg-[#D4AF37]/90 disabled:bg-muted disabled:text-muted-foreground text-[#0F1B33] text-sm font-semibold rounded-lg transition-all duration-200 flex items-center justify-center gap-2 shadow-sm hover:shadow-md"
            >
              {isBuildingSubmission ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Building Package...
                </>
              ) : submissionBuilt ? (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  Package Ready
                </>
              ) : (
                <>
                  <Package className="w-4 h-4" />
                  Build Submission Package
                </>
              )}
            </button>
          </>
        )}
      </div>
    </div>
  );
}
