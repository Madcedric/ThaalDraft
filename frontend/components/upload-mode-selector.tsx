"use client";

import { Wrench, FileSearch, ArrowRight } from "lucide-react";
import { motion } from "framer-motion";

export type UploadMode = "reconstruction" | "formatting_studio";

interface UploadModeSelectorProps {
  selectedMode: UploadMode | null;
  onSelect: (mode: UploadMode) => void;
  disabled?: boolean;
}

const modes = [
  {
    id: "reconstruction" as const,
    title: "Document Reconstruction",
    description: "Extract structure, parse citations, analyze compliance, and review. Full pipeline from raw manuscript.",
    icon: FileSearch,
    steps: ["Parse & Extract", "Citation Analysis", "Compliance Check", "AI Review", "Format"],
    color: "from-blue-500 to-cyan-500",
  },
  {
    id: "formatting_studio" as const,
    title: "Formatting Studio",
    description: "Already have a structured manuscript? Jump straight to journal formatting and export.",
    icon: Wrench,
    steps: ["Select Template", "Preview", "Customize", "Export"],
    color: "from-purple-500 to-pink-500",
  },
];

export function UploadModeSelector({ selectedMode, onSelect, disabled }: UploadModeSelectorProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {modes.map((mode) => {
        const isSelected = selectedMode === mode.id;
        const Icon = mode.icon;

        return (
          <motion.button
            key={mode.id}
            whileHover={{ scale: disabled ? 1 : 1.02 }}
            whileTap={{ scale: disabled ? 1 : 0.98 }}
            onClick={() => !disabled && onSelect(mode.id)}
            disabled={disabled}
            className={`relative text-left p-6 rounded-xl border-2 transition-all duration-200 ${
              isSelected
                ? "border-primary bg-primary/5 shadow-md"
                : "border-border hover:border-primary/30 hover:bg-muted/50"
            } ${disabled ? "opacity-50 cursor-not-allowed" : "cursor-pointer"}`}
          >
            <div className="flex items-start gap-4">
              <div className={`p-3 rounded-xl bg-gradient-to-br ${mode.color} text-white shrink-0`}>
                <Icon className="w-5 h-5" />
              </div>
              <div className="flex-1 min-w-0">
                <h3 className="text-sm font-semibold text-foreground">{mode.title}</h3>
                <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{mode.description}</p>
                <div className="flex items-center gap-1.5 mt-3 flex-wrap">
                  {mode.steps.map((step, i) => (
                    <span key={i} className="inline-flex items-center gap-1">
                      <span className="text-[10px] px-1.5 py-0.5 rounded bg-muted text-muted-foreground font-medium">
                        {step}
                      </span>
                      {i < mode.steps.length - 1 && (
                        <ArrowRight className="w-3 h-3 text-muted-foreground/50" />
                      )}
                    </span>
                  ))}
                </div>
              </div>
            </div>
            {isSelected && (
              <motion.div
                layoutId="mode-indicator"
                className="absolute top-3 right-3 w-2 h-2 rounded-full bg-primary"
              />
            )}
          </motion.button>
        );
      })}
    </div>
  );
}
