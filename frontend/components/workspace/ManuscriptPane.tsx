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
    <div className="flex-1 h-full bg-background flex flex-col relative">
      {/* Top Header */}
      <div className="h-14 border-b border-border flex items-center justify-between px-6 bg-card/80 backdrop-blur-md sticky top-0 z-10">
        <h1 className="text-lg font-semibold text-foreground tracking-tight">{title}</h1>
        <div className="flex items-center text-xs font-medium">
          {isSaving ? (
            <span className="flex items-center gap-1.5 text-[#D4AF37] bg-[#D4AF37]/10 px-2.5 py-1 rounded-full">
              <RefreshCw className="w-3 h-3 animate-spin" />
              Saving...
            </span>
          ) : (
            <span className="flex items-center gap-1.5 text-emerald-600 bg-emerald-50 px-2.5 py-1 rounded-full">
              <Save className="w-3 h-3" />
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
            className="w-full h-full min-h-[800px] bg-transparent text-foreground text-base md:text-lg leading-relaxed focus:outline-none resize-none placeholder-muted-foreground/40"
            placeholder="Start writing your manuscript here..."
            spellCheck="false"
          />
        </div>
      </div>
    </div>
  );
}
