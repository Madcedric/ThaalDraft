import React from 'react';
import { Activity, BookOpen, AlertCircle, CheckCircle2 } from 'lucide-react';

interface AnalysisPaneProps {
  healthScore: number;
  citationsCount: number;
  issuesCount: number;
  mode: 'reconstruction' | 'formatting';
  onModeChange: (mode: 'reconstruction' | 'formatting') => void;
}

export function AnalysisPane({ healthScore, citationsCount, issuesCount, mode, onModeChange }: AnalysisPaneProps) {
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

      <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
        {/* Health Score Card */}
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

        {/* Citations Card */}
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
      </div>
    </div>
  );
}
