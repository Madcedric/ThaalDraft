"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { CheckCircle2, Circle, Loader2, AlertCircle } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";

export interface JobStep {
  id: string;
  label: string;
  status: "pending" | "running" | "completed" | "failed";
  progress?: number;
  message?: string;
  started_at?: string;
  completed_at?: string;
}

interface JobProgressTrackerProps {
  steps: JobStep[];
  title?: string;
  showTimestamps?: boolean;
}

const statusConfig = {
  pending: { icon: Circle, color: "text-muted-foreground", bgColor: "bg-muted" },
  running: { icon: Loader2, color: "text-primary", bgColor: "bg-primary/10" },
  completed: { icon: CheckCircle2, color: "text-emerald-500", bgColor: "bg-emerald-500/10" },
  failed: { icon: AlertCircle, color: "text-destructive", bgColor: "bg-destructive/10" },
};

export function JobProgressTracker({ steps, title = "Processing", showTimestamps = false }: JobProgressTrackerProps) {
  const completedCount = steps.filter((s) => s.status === "completed").length;
  const failedCount = steps.filter((s) => s.status === "failed").length;
  const overallProgress = steps.length > 0 ? (completedCount / steps.length) * 100 : 0;

  return (
    <Card>
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <CardTitle className="text-sm font-semibold">{title}</CardTitle>
          <span className="text-xs text-muted-foreground">
            {completedCount}/{steps.length} completed
            {failedCount > 0 && ` · ${failedCount} failed`}
          </span>
        </div>
        {/* Progress bar */}
        <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden mt-2">
          <motion.div
            className="h-full bg-primary rounded-full"
            initial={{ width: 0 }}
            animate={{ width: `${overallProgress}%` }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="space-y-1">
          <AnimatePresence>
            {steps.map((step, index) => {
              const config = statusConfig[step.status];
              const Icon = config.icon;

              return (
                <motion.div
                  key={step.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 10 }}
                  transition={{ delay: index * 0.05 }}
                  className={`flex items-start gap-3 p-2.5 rounded-lg ${config.bgColor} transition-colors`}
                >
                  <div className="mt-0.5 shrink-0">
                    <Icon
                      className={`w-4 h-4 ${config.color} ${
                        step.status === "running" ? "animate-spin" : ""
                      }`}
                    />
                  </div>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between">
                      <p className="text-sm font-medium text-foreground">{step.label}</p>
                      {showTimestamps && step.completed_at && (
                        <span className="text-[10px] text-muted-foreground">
                          {new Date(step.completed_at).toLocaleTimeString()}
                        </span>
                      )}
                    </div>
                    {step.message && (
                      <p className="text-xs text-muted-foreground mt-0.5 truncate">{step.message}</p>
                    )}
                    {step.status === "running" && step.progress !== undefined && (
                      <div className="w-full h-1 bg-muted rounded-full overflow-hidden mt-1.5">
                        <motion.div
                          className="h-full bg-primary rounded-full"
                          animate={{ width: `${step.progress}%` }}
                          transition={{ duration: 0.3 }}
                        />
                      </div>
                    )}
                  </div>
                </motion.div>
              );
            })}
          </AnimatePresence>
        </div>
      </CardContent>
    </Card>
  );
}
