import { cva, type VariantProps } from "class-variance-authority";
import { cn } from "@/lib/utils";

const statusBadgeVariants = cva(
  "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium transition-colors",
  {
    variants: {
      status: {
        uploaded: "bg-muted text-muted-foreground",
        parsing: "bg-blue-50 text-blue-600 border border-blue-200",
        parsed: "bg-blue-50 text-blue-600 border border-blue-200",
        classifying: "bg-purple-50 text-purple-600 border border-purple-200",
        classified: "bg-purple-50 text-purple-600 border border-purple-200",
        structuring: "bg-indigo-50 text-indigo-600 border border-indigo-200",
        structured: "bg-indigo-50 text-indigo-600 border border-indigo-200",
        formatting: "bg-emerald-50 text-emerald-600 border border-emerald-200",
        formatted: "bg-emerald-50 text-emerald-600 border border-emerald-200",
        failed: "bg-red-50 text-red-600 border border-red-200",
        pending: "bg-muted text-muted-foreground",
        started: "bg-blue-50 text-blue-600 border border-blue-200",
        completed: "bg-emerald-50 text-emerald-600 border border-emerald-200",
        processing: "bg-amber-50 text-amber-600 border border-amber-200",
      },
    },
    defaultVariants: {
      status: "uploaded",
    },
  }
);

export interface StatusBadgeProps extends VariantProps<typeof statusBadgeVariants> {
  label?: string;
  className?: string;
}

const statusLabels: Record<string, string> = {
  uploaded: "Uploaded",
  parsing: "Parsing",
  parsed: "Parsed",
  classifying: "Classifying",
  classified: "Classified",
  structuring: "Structuring",
  structured: "Structured",
  formatting: "Formatting",
  formatted: "Formatted",
  failed: "Failed",
  pending: "Pending",
  started: "In Progress",
  completed: "Completed",
  processing: "Processing",
};

export function StatusBadge({ status, label, className }: StatusBadgeProps) {
  return (
    <span className={cn(statusBadgeVariants({ status }), className)}>
      <span className="flex items-center gap-1.5">
        {status === "processing" || status === "parsing" || status === "formatting" || status === "structuring" || status === "classifying" ? (
          <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
        ) : null}
        {label || statusLabels[status || "uploaded"] || status}
      </span>
    </span>
  );
}
