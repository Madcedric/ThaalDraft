"use client";

import { useState } from "react";
import { UploadCloud, FileType, CheckCircle2, ChevronRight, AlertCircle, LayoutTemplate } from "lucide-react";
import { motion, AnimatePresence } from "framer-motion";
import { useAuth } from "@/lib/auth-context";

export default function DashboardPage() {
  const { user } = useAuth();
  const [file, setFile] = useState<File | null>(null);
  const [template, setTemplate] = useState("ieee");
  const [isProcessing, setIsProcessing] = useState(false);
  const [isDone, setIsDone] = useState(false);
  const [downloadUrl, setDownloadUrl] = useState<string | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  // Process Visualization State
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

      // Simulate steps for UI UX
      setTimeout(() => setProcessStep(2), 800);
      setTimeout(() => setProcessStep(3), 1600);
      
      const response = await fetch("http://localhost:8000/api/v1/documents/format", {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${token}`
        },
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || "Failed to process the document.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      setDownloadUrl(url);
      setProcessStep(4);
      setTimeout(() => {
        setIsDone(true);
        setIsProcessing(false);
      }, 500);
    } catch (error: any) {
      setErrorMessage(error.message || "An unexpected error occurred.");
      setIsProcessing(false);
      setProcessStep(0);
    }
  };

  const templates = [
    { id: "ieee", name: "IEEE Standard", desc: "Two-column technical format" },
    { id: "apa", name: "APA 7th Edition", desc: "Standard psychological format" },
    { id: "nature", name: "Nature Journal", desc: "Single-column scientific" },
  ];

  return (
    <div className="max-w-5xl mx-auto space-y-8 pb-12">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-semibold tracking-tight text-slate-900">New Publication</h1>
        <p className="text-slate-600 mt-1 font-medium">Convert your raw manuscript into a camera-ready journal format.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Main Process Area */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* Upload Card */}
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-white rounded-2xl shadow-md border border-slate-200 p-8"
          >
            <h3 className="text-lg font-bold text-slate-900 mb-4">1. Upload Manuscript</h3>
            
            <div className={`relative border-2 border-dashed rounded-xl p-12 flex flex-col items-center justify-center transition-all duration-200
                ${file ? 'border-indigo-500 bg-indigo-50/50' : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50'}
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
                  <motion.div 
                    key="empty"
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    exit={{ scale: 0.9, opacity: 0 }}
                    className="flex flex-col items-center pointer-events-none"
                  >
                    <div className="p-4 bg-white shadow-sm rounded-full mb-4 border border-slate-200">
                      <UploadCloud className="w-8 h-8 text-indigo-600" />
                    </div>
                    <p className="text-sm font-semibold text-slate-900">Drag & drop your .docx file</p>
                    <p className="text-xs font-medium text-slate-500 mt-1">or click to browse from your computer</p>
                  </motion.div>
                ) : (
                  <motion.div 
                    key="file"
                    initial={{ scale: 0.9, opacity: 0 }}
                    animate={{ scale: 1, opacity: 1 }}
                    className="flex flex-col items-center pointer-events-none"
                  >
                    <div className="p-4 bg-white shadow-sm rounded-full mb-4 border border-indigo-100">
                      <FileType className="w-8 h-8 text-indigo-600" />
                    </div>
                    <p className="text-base font-medium text-slate-900 truncate max-w-[250px]">{file.name}</p>
                    <p className="text-xs text-slate-500 mt-1">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </motion.div>

          {/* Template Selection */}
          <motion.div 
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="bg-white rounded-2xl shadow-md border border-slate-200 p-8"
          >
            <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center">
              2. Select Target Journal
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
              {templates.map((t) => (
                <button
                  key={t.id}
                  onClick={() => setTemplate(t.id)}
                  disabled={isProcessing}
                  className={`text-left p-4 rounded-xl border-2 transition-all duration-200 focus:outline-none
                    ${template === t.id 
                      ? 'border-indigo-600 bg-indigo-50 shadow-md' 
                      : 'border-slate-300 hover:border-indigo-400 hover:bg-slate-50 shadow-sm'}
                  `}
                >
                  <div className="flex justify-between items-start mb-2">
                    <LayoutTemplate className={`w-5 h-5 ${template === t.id ? 'text-indigo-600' : 'text-slate-500'}`} />
                    {template === t.id && <CheckCircle2 className="w-4 h-4 text-indigo-600" />}
                  </div>
                  <h4 className={`font-semibold text-sm ${template === t.id ? 'text-indigo-900' : 'text-slate-800'}`}>{t.name}</h4>
                  <p className="text-xs font-medium text-slate-600 mt-1">{t.desc}</p>
                </button>
              ))}
            </div>
          </motion.div>

        </div>

        {/* Sidebar Status Area */}
        <div className="lg:col-span-1">
          <motion.div 
            initial={{ opacity: 0, x: 10 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="bg-white rounded-2xl shadow-md border border-slate-200 p-6 sticky top-24"
          >
            <h3 className="font-bold text-slate-900 mb-6">Execution Flow</h3>

            {/* Steps Visualization */}
            <div className="space-y-6 mb-8 relative before:absolute before:inset-0 before:ml-[11px] before:-translate-x-px before:h-full before:w-0.5 before:bg-gradient-to-b before:from-transparent before:via-slate-300 before:to-transparent">
              
              <div className="relative flex items-center group">
                <div className={`flex items-center justify-center w-6 h-6 rounded-full border-2 bg-white z-10 shrink-0
                  ${processStep >= 1 ? 'border-indigo-600' : 'border-slate-400'}`}>
                  {processStep >= 1 && <div className="w-2 h-2 bg-indigo-600 rounded-full" />}
                </div>
                <div className="ml-4">
                  <h4 className={`text-sm font-semibold ${processStep >= 1 ? 'text-indigo-900' : 'text-slate-500'}`}>Upload Document</h4>
                </div>
              </div>

              <div className="relative flex items-center group">
                <div className={`flex items-center justify-center w-6 h-6 rounded-full border-2 bg-white z-10 shrink-0
                  ${processStep >= 2 ? 'border-indigo-600' : 'border-slate-400'}`}>
                  {processStep >= 2 && <div className="w-2 h-2 bg-indigo-600 rounded-full" />}
                </div>
                <div className="ml-4">
                  <h4 className={`text-sm font-semibold ${processStep >= 2 ? 'text-indigo-900' : 'text-slate-500'}`}>Parse Structure</h4>
                </div>
              </div>

              <div className="relative flex items-center group">
                <div className={`flex items-center justify-center w-6 h-6 rounded-full border-2 bg-white z-10 shrink-0
                  ${processStep >= 3 ? 'border-indigo-600' : 'border-slate-400'}`}>
                  {processStep >= 3 && <div className="w-2 h-2 bg-indigo-600 rounded-full" />}
                </div>
                <div className="ml-4">
                  <h4 className={`text-sm font-semibold ${processStep >= 3 ? 'text-indigo-900' : 'text-slate-500'}`}>AI Formatting</h4>
                </div>
              </div>

              <div className="relative flex items-center group">
                <div className={`flex items-center justify-center w-6 h-6 rounded-full border-2 bg-white z-10 shrink-0
                  ${processStep >= 4 ? 'border-emerald-600 bg-emerald-50' : 'border-slate-400'}`}>
                  {processStep >= 4 && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />}
                </div>
                <div className="ml-4">
                  <h4 className={`text-sm font-semibold ${processStep >= 4 ? 'text-emerald-700' : 'text-slate-500'}`}>Ready</h4>
                </div>
              </div>
            </div>

            {/* Error Message */}
            {errorMessage && (
              <motion.div 
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                className="mb-6 p-4 bg-red-50 text-red-700 text-sm rounded-lg border border-red-100 flex items-start"
              >
                <AlertCircle className="w-5 h-5 mr-2 shrink-0" />
                <p>{errorMessage}</p>
              </motion.div>
            )}

            {/* Actions */}
            {!isDone ? (
              <button 
                className={`w-full h-12 flex items-center justify-center text-sm font-medium transition-all rounded-xl relative overflow-hidden group
                  ${!file || isProcessing || !user ? 'bg-slate-100 text-slate-400 cursor-not-allowed' : 'bg-indigo-600 hover:bg-indigo-700 text-white shadow-md hover:shadow-lg'}`}
                onClick={handleUpload}
                disabled={!file || isProcessing || !user}
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
              </button>
            ) : (
              <a 
                href={downloadUrl || "#"} 
                download={file ? `formatted_${file.name}` : "formatted_document.docx"}
                className="w-full h-12 flex items-center justify-center text-sm font-medium bg-emerald-600 hover:bg-emerald-700 text-white shadow-md hover:shadow-lg transition-all rounded-xl" 
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
              </a>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
