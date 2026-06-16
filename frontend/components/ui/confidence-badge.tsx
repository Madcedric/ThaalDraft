import { cn } from "@/lib/utils";

interface ConfidenceBadgeProps {
  confidence: number;
  className?: string;
  showLabel?: boolean;
}

function getConfidenceLevel(confidence: number): { label: string; color: string; bgColor: string } {
  if (confidence >= 0.9) {
    return { label: "High", color: "text-emerald-700", bgColor: "bg-emerald-50 border-emerald-200" };
  }
  if (confidence >= 0.7) {
    return { label: "Medium", color: "text-amber-700", bgColor: "bg-amber-50 border-amber-200" };
  }
  return { label: "Low", color: "text-red-700", bgColor: "bg-red-50 border-red-200" };
}

export function ConfidenceBadge({ confidence, className, showLabel = true }: ConfidenceBadgeProps) {
  const { label, color, bgColor } = getConfidenceLevel(confidence);
  const percentage = Math.round(confidence * 100);

  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 rounded-full border px-2 py-0.5 text-xs font-medium",
        bgColor,
        color,
        className
      )}
    >
      <span className="w-1.5 h-1.5 rounded-full bg-current" />
      {showLabel && <span>{label}</span>}
      <span className="font-semibold">{percentage}%</span>
    </span>
  );
}
