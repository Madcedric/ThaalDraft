import React from 'react';
import { AlignLeft, Layers, ListTree } from 'lucide-react';

interface StructurePaneProps {
  sections: { id: string; title: string; level: number }[];
  activeSection: string;
  onSectionClick: (id: string) => void;
}

export function StructurePane({ sections, activeSection, onSectionClick }: StructurePaneProps) {
  return (
    <div className="w-64 h-full bg-zinc-900 border-r border-zinc-800 flex flex-col hidden md:flex">
      <div className="h-14 border-b border-zinc-800 flex items-center px-4 shrink-0">
        <ListTree className="w-4 h-4 text-zinc-400 mr-2" />
        <h2 className="text-sm font-medium text-zinc-200">Document Outline</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto py-4 px-2 custom-scrollbar">
        {sections.length === 0 ? (
          <div className="text-xs text-zinc-500 px-2 text-center mt-10">No outline available yet</div>
        ) : (
          <ul className="space-y-1">
            {sections.map((sec) => (
              <li key={sec.id}>
                <button
                  onClick={() => onSectionClick(sec.id)}
                  className={`w-full text-left px-2 py-1.5 text-sm rounded-md transition-all duration-200 flex items-center group
                    ${activeSection === sec.id 
                      ? 'bg-zinc-800 text-zinc-100 font-medium shadow-sm' 
                      : 'text-zinc-400 hover:bg-zinc-800/50 hover:text-zinc-200'
                    }`}
                  style={{ paddingLeft: `${(sec.level - 1) * 12 + 8}px` }}
                >
                  <AlignLeft className={`w-3.5 h-3.5 mr-2 opacity-50 group-hover:opacity-100 transition-opacity ${activeSection === sec.id ? 'text-blue-400' : ''}`} />
                  <span className="truncate">{sec.title}</span>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
}
