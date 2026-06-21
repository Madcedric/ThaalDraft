import React from 'react';
import { AlignLeft, ListTree } from 'lucide-react';

interface StructurePaneProps {
  sections: { id: string; title: string; level: number }[];
  activeSection: string;
  onSectionClick: (id: string) => void;
}

export function StructurePane({ sections, activeSection, onSectionClick }: StructurePaneProps) {
  return (
    <div className="w-64 h-full bg-card border-r border-border flex flex-col hidden md:flex">
      <div className="h-14 border-b border-border flex items-center px-4 shrink-0 bg-card">
        <ListTree className="w-4 h-4 text-[#D4AF37] mr-2" />
        <h2 className="text-sm font-medium text-foreground">Document Outline</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto py-4 px-2 custom-scrollbar">
        {sections.length === 0 ? (
          <div className="text-xs text-muted-foreground px-2 text-center mt-10">No outline available yet</div>
        ) : (
          <ul className="space-y-1">
            {sections.map((sec) => (
              <li key={sec.id}>
                <button
                  onClick={() => onSectionClick(sec.id)}
                  className={`w-full text-left px-2 py-1.5 text-sm rounded transition-all duration-200 flex items-center group
                    ${activeSection === sec.id 
                      ? 'bg-[#D4AF37]/10 text-[#D4AF37] font-medium' 
                      : 'text-muted-foreground hover:bg-muted hover:text-foreground'
                    }`}
                  style={{ paddingLeft: `${(sec.level - 1) * 12 + 8}px` }}
                >
                  <AlignLeft className={`w-3.5 h-3.5 mr-2 opacity-50 group-hover:opacity-100 transition-opacity ${activeSection === sec.id ? 'text-[#D4AF37]' : ''}`} />
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
