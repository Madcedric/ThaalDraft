"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { UploadCloud, FileText, CheckCircle2, ChevronRight, AlertCircle, LayoutTemplate } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/lib/auth-context";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";

export default function DashboardPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [template, setTemplate] = useState("ieee");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDone, setIsDone] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [processStep, setProcessStep] = useState(0);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setIsDone(false);
    }
  };

  const handleUpload = async () => {
    if (!file || !user) return;
    setIsProcessing(true);
    setErrorMessage(null);
    setProcessStep(1);

    try {
      const token = await user.getIdToken();
      const formData = new FormData();
      formData.append("file", file);
      formData.append("template", template);

      setTimeout(() => setProcessStep(2), 800);
      setTimeout(() => setProcessStep(3), 1600);

      const response = await fetch((process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000") + "/api/v1/documents/upload", {
        method: "POST",
        headers: { "Authorization": `Bearer ${token}` },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to upload the document.");
      }

      const data = await response.json();
      const docId = data.id || data.id;
      setProcessStep(4);
      router.push(`/dashboard/reports?docId=${docId}`);
    } catch (error: unknown) {
      const message = error instanceof Error ? error.message : "An unexpected error occurred.";
      setErrorMessage(message);
      setIsProcessing(false);
      setProcessStep(0);
    }
  };

  const templates = [
    { id: "ieee", name: "IEEE Standard", desc: "Two-column technical format" },
    { id: "apa", name: "APA 7th Edition", desc: "Standard psychological format" },
    { id: "nature", name: "Nature Journal", desc: "Single-column scientific" },
  ];

  const steps = [
    { label: "Upload Document", active: processStep >= 1 },
    { label: "Parse Structure", active: processStep >= 2 },
    { label: "AI Formatting", active: processStep >= 3 },
    { label: "Ready", active: processStep >= 4, success: processStep >= 4 },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-foreground">New Publication</h1>
        <p className="text-muted-foreground mt-1 font-medium">Convert your raw manuscript into a camera-ready journal format.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
            <Card>
              <CardHeader>
                <CardTitle className="text-base">1. Upload Manuscript</CardTitle>
              </CardHeader>
              <CardContent>
                <div className={`relative border-2 border-dashed rounded-xl p-12 flex flex-col items-center justify-center transition-all duration-200
                    ${file ? 'border-primary bg-primary/5' : 'border-border hover:border-primary/50 hover:bg-muted/50'}
                    ${isProcessing ? 'opacity-50 pointer-events-none' : ''}`}>
                  <input
                    type="file"
                    accept=".docx"
                    onChange={handleFileChange}
                    disabled={isProcessing}
                    className="absolute inset-0 w-full h-full opacity-0 cursor-pointer disabled:cursor-not-allowed z-10"
                  />
                  <AnimatePresence mode="wait">
                    {!file ? (
                      <motion.div key="empty" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.9, opacity: 0 }} className="flex flex-col items-center pointer-events-none">
                        <div className="p-4 bg-card shadow-sm rounded-full mb-4 border border-border">
                          <UploadCloud className="w-8 h-8 text-primary" />
                        </div>
                        <p className="text-sm font-semibold text-foreground">Drag & drop your .docx file</p>
                        <p className="text-xs font-medium text-muted-foreground mt-1">or click to browse from your computer</p>
                      </motion.div>
                    ) : (
                      <motion.div key="file" initial={{ scale: 0.9, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} className="flex flex-col items-center pointer-events-none">
                        <div className="p-4 bg-card shadow-sm rounded-full mb-4 border border-primary/20">
                          <FileText className="w-8 h-8 text-primary" />
                        </div>
                        <p className="text-base font-medium text-foreground truncate max-w-[250px]">{file.name}</p>
                        <p className="text-xs text-muted-foreground mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              </CardContent>
            </Card>
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
            <Card>
              <CardHeader>
                <CardTitle className="text-base flex items-center gap-2">2. Select Target Journal</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  {templates.map((t) => (
                    <button
                      key={t.id}
                      onClick={() => setTemplate(t.id)}
                      disabled={isProcessing}
                      className={`text-left p-4 rounded-xl border-2 transition-all duration-200 focus:outline-none focus-visible:ring-2 focus-visible:ring-ring
                        ${template === t.id
                          ? 'border-primary bg-primary/5 shadow-md'
                          : 'border-border hover:border-primary/50 hover:bg-muted/50 shadow-sm'
                        }`}
                    >
                      <div className="flex justify-between items-start mb-2">
                        <LayoutTemplate className={`w-5 h-5 ${template === t.id ? 'text-primary' : 'text-muted-foreground'}`} />
                        {template === t.id && <CheckCircle2 className="w-4 h-4 text-primary" />}
                      </div>
                      <h4 className={`font-semibold text-sm ${template === t.id ? 'text-foreground' : 'text-foreground'}`}>{t.name}</h4>
                      <p className="text-xs font-medium text-muted-foreground mt-1">{t.desc}</p>
                    </button>
                  ))}
                </div>
              </CardContent>
            </Card>
          </motion.div>
        </div>

        <div className="lg:col-span-1">
          <motion.div initial={{ opacity: 0, x: 10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}>
            <Card className="sticky top-24">
              <CardHeader>
                <CardTitle className="text-sm">Execution Flow</CardTitle>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="space-y-4 relative before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px before:h-full before:w-0.5 before:bg-border">
                  {steps.map((step, i) => (
                    <div key={i} className="relative flex items-center">
                      <div className={`flex items-center justify-center w-6 h-6 rounded-full border-2 bg-card z-10 shrink-0 transition-colors
                        ${step.success ? 'border-green-600 bg-green-50' : step.active ? 'border-primary' : 'border-muted-foreground/30'}`}>
                        {step.success ? (
                          <CheckCircle2 className="w-3.5 h-3.5 text-green-600" />
                        ) : step.active ? (
                          <div className="w-2 h-2 bg-primary rounded-full" />
                        ) : null}
                      </div>
                      <div className="ml-4">
                        <h4 className={`text-sm font-semibold ${step.active ? (step.success ? 'text-green-600' : 'text-foreground') : 'text-muted-foreground'}`}>{step.label}</h4>
                      </div>
                    </div>
                  ))}
                </div>

                {errorMessage && (
                  <Alert variant="destructive">
                    <AlertCircle className="h-4 w-4" />
                    <AlertDescription className="text-sm">{errorMessage}</AlertDescription>
                  </Alert>
                )}

                {!isDone ? (
                  <Button
                    className="w-full h-11 relative overflow-hidden group"
                    disabled={!file || isProcessing || !user}
                    onClick={handleUpload}
                  >
                    {isProcessing && (
                      <motion.div
                        initial={{ x: '-100%' }}
                        animate={{ x: '100%' }}
                        transition={{ repeat: Infinity, duration: 1.5, ease: "linear" }}
                        className="absolute inset-0 bg-white/20 skew-x-12"
                      />
                    )}
                    <span className="relative z-10 flex items-center">
                      {isProcessing ? "Processing..." : "Generate Publication"}
                      {!isProcessing && <ChevronRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />}
                    </span>
                  </Button>
                ) : (
                  <Button
                    variant="default"
                    className="w-full h-11 bg-green-600 hover:bg-green-700 text-white"
                    onClick={() => {
                      setTimeout(() => {
                        setIsDone(false);
                        setFile(null);
                        setProcessStep(0);
                        if (downloadUrl) window.URL.revokeObjectURL(downloadUrl);
                        setDownloadUrl(null);
                      }, 500);
                    }}
                  >
                    <CheckCircle2 className="mr-2 h-4 w-4" />
                    Download Camera-Ready DOCX
                  </Button>
                )}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
