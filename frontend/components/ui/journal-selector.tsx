import { cn } from "@/lib/utils";
import { CheckCircle2, ExternalLink } from "lucide-react";

export interface Journal {
  id: string;
  name: string;
  shortName: string;
  citationStyle: string;
  description: string;
  url?: string;
}

export const JOURNALS: Journal[] = [
  {
    id: "ieee",
    name: "IEEE",
    shortName: "IEEE",
    citationStyle: "IEEE",
    description: "Two-column technical format for engineering and computer science",
    url: "https://www.ieee.org",
  },
  {
    id: "acm",
    name: "ACM",
    shortName: "ACM",
    citationStyle: "ACM",
    description: "Computer science conference proceedings format",
    url: "https://www.acm.org",
  },
  {
    id: "springer",
    name: "Springer LNCS",
    shortName: "Springer",
    citationStyle: "Springer",
    description: "Lecture Notes in Computer Science format",
    url: "https://www.springer.com",
  },
  {
    id: "elsevier",
    name: "Elsevier",
    shortName: "Elsevier",
    citationStyle: "Elsevier",
    description: "Scientific journal format for Elsevier publications",
    url: "https://www.elsevier.com",
  },
  {
    id: "apa",
    name: "APA 7th Edition",
    shortName: "APA",
    citationStyle: "APA",
    description: "American Psychological Association formatting standard",
    url: "https://apastyle.apa.org",
  },
  {
    id: "mla",
    name: "MLA 9th Edition",
    shortName: "MLA",
    citationStyle: "MLA",
    description: "Modern Language Association humanities formatting",
    url: "https://www.mla.org",
  },
  {
    id: "nature",
    name: "Nature",
    shortName: "Nature",
    citationStyle: "Nature",
    description: "Single-column scientific journal format",
    url: "https://www.nature.com",
  },
  {
    id: "custom",
    name: "Custom Format",
    shortName: "Custom",
    citationStyle: "Custom",
    description: "Define your own formatting rules",
  },
];

interface JournalSelectorProps {
  selectedJournalId: string;
  onSelect: (journal: Journal) => void;
  className?: string;
  disabled?: boolean;
}

export function JournalSelector({ selectedJournalId, onSelect, className, disabled }: JournalSelectorProps) {
  return (
    <div className={cn("space-y-3", className)}>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
        {JOURNALS.map((journal) => {
          const isSelected = selectedJournalId === journal.id;
          return (
            <button
              key={journal.id}
              onClick={() => onSelect(journal)}
              disabled={disabled}
              className={cn(
                "text-left p-3 rounded-xl border-2 transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring",
                isSelected
                  ? "border-primary bg-primary/5 shadow-md"
                  : "border-border hover:border-primary/50 hover:bg-muted/50 shadow-sm",
                disabled && "opacity-50 cursor-not-allowed"
              )}
              aria-pressed={isSelected}
              aria-label={`Select ${journal.name} format`}
            >
              <div className="flex justify-between items-start mb-2">
                <span className="text-xs font-semibold text-primary uppercase tracking-wider">
                  {journal.shortName}
                </span>
                {isSelected && <CheckCircle2 className="w-4 h-4 text-primary shrink-0" />}
              </div>
              <h4 className="font-semibold text-sm text-foreground leading-tight">{journal.name}</h4>
              <p className="text-xs text-muted-foreground mt-1 line-clamp-2">{journal.description}</p>
              <div className="flex items-center gap-1 mt-2">
                <span className="text-xs text-muted-foreground">Style: {journal.citationStyle}</span>
                {journal.url && (
                  <ExternalLink className="w-3 h-3 text-muted-foreground/50" />
                )}
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

export function getJournalById(id: string): Journal | undefined {
  return JOURNALS.find((j) => j.id === id);
}
