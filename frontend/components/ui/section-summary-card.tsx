import { cn } from "@/lib/utils";
import { ConfidenceBadge } from "@/components/ui/confidence-badge";
import {
  FileText,
  BookOpen,
  FlaskConical,
  BarChart3,
  MessageSquare,
  CheckCircle2,
  List,
} from "lucide-react";

interface Section {
  heading: string;
  label: string;
  content?: string;
  confidence?: number;
}

interface SectionSummaryCardProps {
  sections: Section[];
  className?: string;
}

const sectionIcons: Record<string, typeof FileText> = {
  abstract: BookOpen,
  introduction: FileText,
  methods: FlaskConical,
  results: BarChart3,
  discussion: MessageSquare,
  conclusion: CheckCircle2,
  references: List,
};

const sectionLabels: Record<string, string> = {
  abstract: "Abstract",
  introduction: "Introduction",
  methods: "Methods",
  results: "Results",
  discussion: "Discussion",
  conclusion: "Conclusion",
  references: "References",
  other: "Other",
};

export function SectionSummaryCard({ sections, className }: SectionSummaryCardProps) {
  const grouped = sections.reduce(
    (acc, section) => {
      const label = section.label || "other";
      if (!acc[label]) acc[label] = [];
      acc[label].push(section);
      return acc;
    },
    {} as Record<string, Section[]>
  );

  const displayOrder = ["abstract", "introduction", "methods", "results", "discussion", "conclusion", "references"];

  return (
    <div className={cn("rounded-xl border border-border bg-card p-4 shadow-sm", className)}>
      <h3 className="text-sm font-semibold text-foreground mb-4">Detected Structure</h3>
      <div className="space-y-3">
        {displayOrder.map((label) => {
          const sectionGroup = grouped[label];
          if (!sectionGroup) return null;

          const Icon = sectionIcons[label] || FileText;
          const avgConfidence =
            sectionGroup.reduce((sum, s) => sum + (s.confidence || 0), 0) / sectionGroup.length;

          return (
            <div key={label} className="flex items-center justify-between py-2 border-b border-border last:border-0">
              <div className="flex items-center gap-3">
                <div className="rounded-lg bg-muted p-1.5">
                  <Icon className="h-4 w-4 text-muted-foreground" />
                </div>
                <div>
                  <p className="text-sm font-medium text-foreground">
                    {sectionLabels[label] || label}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {sectionGroup.length} {sectionGroup.length === 1 ? "section" : "sections"}
                  </p>
                </div>
              </div>
              {avgConfidence > 0 && <ConfidenceBadge confidence={avgConfidence} />}
            </div>
          );
        })}
      </div>
    </div>
  );
}
