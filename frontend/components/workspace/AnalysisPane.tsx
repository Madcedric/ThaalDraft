import React, { useState, useEffect } from 'react';
import { Activity, BookOpen, AlertCircle, CheckCircle2, Download, FileText, Loader2, Send } from 'lucide-react';

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
  const [selectedTemplate, setSelectedTemplate] = useState('ieee');
  const [isExporting, setIsExporting] = useState(false);
  const [exportMessage, setExportMessage] = useState<string | null>(null);

  const handleExport = async (format: string) => {
    if (!documentId) return;
    setIsExporting(true);
    setExportMessage(null);
    try {
      const token = localStorage.getItem('firebase_id_token') || sessionStorage.getItem('firebase_id_token');
      if (!token) { setExportMessage('Not authenticated'); return; }

      const response = await fetch(
        `${process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8000'}/api/v1/documents/${documentId}/export`,
        {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ template: selectedTemplate, format }),
        }
      );

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

  return (
    <div className="w-72 h-full bg-zinc-900 border-l border-zinc-800 flex flex-col hidden lg:flex">
      {/* Mode Selector */}
      <div className="p-4 border-b border-zinc-800">
        <div className="bg-zinc-950 p-1 rounded-lg flex text-xs font-medium border border-zinc-800/50">
          <button
            onClick={() => onModeChange('reconstruction')}
            className={`flex-1 py-1.5 px-2 rounded-md transition-all duration-200 ${
              mode === 'reconstruction'
                ? 'bg-blue-600 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800'
            }`}
          >
            Reconstruct
          </button>
          <button
            onClick={() => onModeChange('formatting')}
            className={`flex-1 py-1.5 px-2 rounded-md transition-all duration-200 ${
              mode === 'formatting'
                ? 'bg-purple-600 text-white shadow-sm'
                : 'text-zinc-400 hover:text-zinc-200 hover:bg-zinc-800'
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
              className="w-full py-2.5 px-3 bg-blue-600 hover:bg-blue-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
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
            <div className="bg-zinc-950/50 border border-zinc-800/80 rounded-xl p-4 shadow-sm">
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 flex items-center">
                  <Activity className="w-3.5 h-3.5 mr-1.5" />
                  Document Health
                </h3>
                <span className={`text-sm font-bold ${healthScore >= 80 ? 'text-emerald-400' : healthScore >= 50 ? 'text-amber-400' : 'text-rose-400'}`}>
                  {healthScore}/100
                </span>
              </div>
              <div className="w-full bg-zinc-800 rounded-full h-1.5">
                <div
                  className={`h-1.5 rounded-full ${healthScore >= 80 ? 'bg-emerald-500' : healthScore >= 50 ? 'bg-amber-500' : 'bg-rose-500'}`}
                  style={{ width: `${healthScore}%` }}
                />
              </div>
            </div>

            {/* Citations */}
            <div className="bg-zinc-950/50 border border-zinc-800/80 rounded-xl p-4 shadow-sm">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 flex items-center mb-3">
                <BookOpen className="w-3.5 h-3.5 mr-1.5" />
                Citations
              </h3>
              <div className="flex items-end justify-between">
                <div>
                  <div className="text-2xl font-semibold text-zinc-200">{citationsCount}</div>
                  <div className="text-xs text-zinc-500 mt-0.5">Total References</div>
                </div>
                {issuesCount > 0 ? (
                  <div className="flex items-center text-xs font-medium text-rose-400 bg-rose-400/10 px-2 py-1 rounded-md">
                    <AlertCircle className="w-3 h-3 mr-1" />
                    {issuesCount} Issues
                  </div>
                ) : (
                  <div className="flex items-center text-xs font-medium text-emerald-400 bg-emerald-400/10 px-2 py-1 rounded-md">
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
            <div className="bg-zinc-950/50 border border-zinc-800/80 rounded-xl p-4 shadow-sm">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 flex items-center mb-3">
                <FileText className="w-3.5 h-3.5 mr-1.5" />
                Journal Template
              </h3>
              <div className="space-y-1.5">
                {TEMPLATES.map((t) => (
                  <button
                    key={t.id}
                    onClick={() => setSelectedTemplate(t.id)}
                    className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-all duration-150 ${
                      selectedTemplate === t.id
                        ? 'bg-purple-600/20 border border-purple-500/30 text-purple-300'
                        : 'bg-zinc-800/50 border border-transparent text-zinc-400 hover:bg-zinc-800 hover:text-zinc-200'
                    }`}
                  >
                    <div className="font-medium">{t.name}</div>
                    <div className="text-xs opacity-60">{t.desc}</div>
                  </button>
                ))}
              </div>
            </div>

            {/* Export Buttons */}
            <div className="bg-zinc-950/50 border border-zinc-800/80 rounded-xl p-4 shadow-sm">
              <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-500 flex items-center mb-3">
                <Download className="w-3.5 h-3.5 mr-1.5" />
                Export
              </h3>
              <div className="space-y-2">
                {EXPORT_FORMATS.map((f) => (
                  <button
                    key={f.id}
                    onClick={() => handleExport(f.id)}
                    disabled={isExporting || !documentId}
                    className="w-full py-2 px-3 bg-zinc-800 hover:bg-zinc-700 disabled:bg-zinc-800 disabled:text-zinc-600 text-zinc-200 text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2 border border-zinc-700"
                  >
                    {isExporting ? (
                      <Loader2 className="w-4 h-4 animate-spin" />
                    ) : (
                      <Download className="w-4 h-4" />
                    )}
                    {f.label} <span className="text-zinc-500 text-xs">{f.ext}</span>
                  </button>
                ))}
              </div>
              {exportMessage && (
                <p className={`text-xs mt-2 text-center ${exportMessage.includes('failed') ? 'text-rose-400' : 'text-emerald-400'}`}>
                  {exportMessage}
                </p>
              )}
            </div>

            {/* Submit to Journal */}
            <button
              disabled={!documentId}
              className="w-full py-2.5 px-3 bg-emerald-600 hover:bg-emerald-500 disabled:bg-zinc-700 disabled:text-zinc-500 text-white text-sm font-medium rounded-lg transition-colors flex items-center justify-center gap-2"
            >
              <Send className="w-4 h-4" />
              Submit to Journal
            </button>
          </>
        )}
      </div>
    </div>
  );
}
