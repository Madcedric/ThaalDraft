import React from 'react';
import { Save, RefreshCw } from 'lucide-react';

interface ManuscriptPaneProps {
  content: string;
  onChange: (newContent: string) => void;
  isSaving?: boolean;
  title?: string;
}

export function ManuscriptPane({ content, onChange, isSaving = false, title = "Untitled Manuscript" }: ManuscriptPaneProps) {
  return (
    <div className="flex-1 h-full bg-zinc-950 flex flex-col relative">
      {/* Top Header */}
      <div className="h-14 border-b border-zinc-800 flex items-center justify-between px-6 bg-zinc-950/80 backdrop-blur-md sticky top-0 z-10">
        <h1 className="text-lg font-semibold text-zinc-100 tracking-tight">{title}</h1>
        <div className="flex items-center text-xs font-medium text-zinc-500">
          {isSaving ? (
            <span className="flex items-center text-blue-400">
              <RefreshCw className="w-3.5 h-3.5 mr-1.5 animate-spin" />
              Saving...
            </span>
          ) : (
            <span className="flex items-center">
              <Save className="w-3.5 h-3.5 mr-1.5 opacity-50" />
              Saved
            </span>
          )}
        </div>
      </div>

      {/* Editor Area */}
      <div className="flex-1 overflow-y-auto px-8 py-10 md:px-20 lg:px-32 flex justify-center custom-scrollbar">
        <div className="w-full max-w-3xl">
          <textarea
            value={content}
            onChange={(e) => onChange(e.target.value)}
            className="w-full h-full min-h-[800px] bg-transparent text-zinc-200 text-base md:text-lg leading-relaxed focus:outline-none resize-none placeholder-zinc-700"
            placeholder="Start writing your manuscript here..."
            spellCheck="false"
          />
        </div>
      </div>
    </div>
  );
}
