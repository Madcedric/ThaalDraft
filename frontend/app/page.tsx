"use client";

import { motion } from "framer-motion";
import { ArrowRight, CheckCircle2, FileText, Zap, Shield, Sparkles, LayoutTemplate, UploadCloud } from "lucide-react";
import Link from "next/link";
import { useAuth } from "@/lib/auth-context";

export default function LandingPage() {
  const { user, loading } = useAuth();

  return (
    <div className="min-h-screen bg-slate-50 selection:bg-indigo-100 selection:text-indigo-900">
      
      {/* Navigation */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-slate-200 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-lg flex items-center justify-center">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <span className="text-xl font-bold text-slate-900 tracking-tight">ManuscriptAI</span>
          </div>
          <div className="hidden md:flex space-x-8">
            <a href="#features" className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">Features</a>
            <a href="#demo" className="text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">How it Works</a>
          </div>
          <div className="flex items-center space-x-4">
            {loading ? (
              <div className="h-9 w-24 bg-slate-100 rounded-full animate-pulse" />
            ) : user ? (
              <Link href="/dashboard" className="px-4 py-2 bg-indigo-600 text-white text-sm font-medium rounded-full hover:bg-indigo-700 transition-all shadow-sm hover:shadow">
                Go to Dashboard
              </Link>
            ) : (
              <>
                <Link href="/login" className="hidden sm:block text-sm font-medium text-slate-600 hover:text-indigo-600 transition-colors">Log in</Link>
                <Link href="/login" className="px-4 py-2 bg-slate-900 text-white text-sm font-medium rounded-full hover:bg-slate-800 transition-all shadow-sm hover:shadow">
                  Get Started
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto text-center space-y-8">
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-indigo-50 border border-indigo-100 text-indigo-600 text-sm font-medium mb-4"
          >
            <Sparkles className="w-4 h-4" />
            <span>AI-Powered Formatting Engine 2.0 Live</span>
          </motion.div>
          
          <motion.h1 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold text-slate-900 tracking-tight max-w-4xl mx-auto leading-[1.1]"
          >
            Publish Faster. <span className="text-transparent bg-clip-text bg-gradient-to-r from-indigo-600 to-violet-600">Format Smarter.</span>
          </motion.h1>
          
          <motion.p 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg md:text-xl text-slate-500 max-w-2xl mx-auto"
          >
            Instantly convert your raw DOCX manuscripts into publication-ready IEEE, ACM, and Springer formats using intelligent AI automation.
          </motion.p>
          
          <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4"
          >
            <Link href={user ? "/dashboard" : "/login"} className="w-full sm:w-auto px-8 py-4 bg-indigo-600 text-white font-medium rounded-full hover:bg-indigo-700 transition-all shadow-lg hover:shadow-xl hover:-translate-y-0.5 flex items-center justify-center group">
              Convert to IEEE / ACM
              <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
            </Link>
            <Link href="#demo" className="w-full sm:w-auto px-8 py-4 bg-white text-slate-700 font-medium rounded-full border border-slate-200 hover:bg-slate-50 transition-all flex items-center justify-center">
              View Demo
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Interactive Drag & Drop Preview */}
      <section className="pb-24 px-6 relative z-10 -mt-8 hidden md:block">
        <motion.div 
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.4 }}
          className="max-w-4xl mx-auto bg-white rounded-2xl shadow-2xl border border-slate-100 overflow-hidden"
        >
          <div className="bg-slate-50 border-b border-slate-100 p-4 flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-400"></div>
            <div className="w-3 h-3 rounded-full bg-amber-400"></div>
            <div className="w-3 h-3 rounded-full bg-green-400"></div>
          </div>
          <Link href={user ? "/dashboard" : "/login"} className="block p-12 border-2 border-dashed border-indigo-100 mx-8 my-8 rounded-xl bg-indigo-50/30 flex flex-col items-center justify-center text-center group hover:border-indigo-300 hover:bg-indigo-50/50 transition-colors cursor-pointer">
            <div className="w-16 h-16 bg-white rounded-full shadow-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300">
              <UploadCloud className="w-8 h-8 text-indigo-600" />
            </div>
            <h3 className="text-xl font-semibold text-slate-800 mb-2">Drag your manuscript here</h3>
            <p className="text-slate-500 max-w-sm">We'll automatically detect headings, citations, and structure to generate a perfectly formatted academic paper.</p>
          </Link>
        </motion.div>
      </section>

      {/* Before / After Section */}
      <section id="demo" className="py-24 bg-white px-6 border-t border-slate-100">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">From Draft to Camera-Ready</h2>
            <p className="text-slate-500 max-w-2xl mx-auto text-lg">See the intelligence in action. We transform unstructured text into strictly compliant journal formats.</p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 items-center max-w-5xl mx-auto">
            <div className="bg-slate-50 rounded-2xl p-8 border border-slate-200 relative h-72">
              <div className="absolute top-4 right-4 bg-slate-200 text-slate-600 text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">Before</div>
              <div className="font-mono text-sm text-slate-600 space-y-4 opacity-70 pt-8">
                <p className="font-bold text-lg">AI in Healthcare: A Comprehensive Review</p>
                <p>abstract: This paper explores the integration of artificial intelligence in modern clinical settings...</p>
                <p className="uppercase mt-6">Introduction</p>
                <p>Recently there has been a surge in machine learning applications...</p>
              </div>
            </div>
            <div className="bg-indigo-50 rounded-2xl p-8 border border-indigo-100 relative shadow-inner h-72">
              <div className="absolute top-4 right-4 bg-indigo-600 text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">After (IEEE)</div>
              <div className="font-serif text-sm text-slate-900 flex flex-col items-center text-center space-y-4 pt-8">
                <h1 className="text-xl font-bold">AI in Healthcare: A Comprehensive Review</h1>
                <p className="italic text-xs px-8 text-justify">Abstract—This paper explores the integration of artificial intelligence in modern clinical settings...</p>
                <h2 className="text-sm font-bold uppercase tracking-widest mt-4">I. Introduction</h2>
                <p className="text-left text-xs leading-relaxed text-justify indent-4 w-full px-8">Recently there has been a surge in machine learning applications...</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 px-6 bg-slate-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-slate-900 mb-4">Built for Academics</h2>
            <p className="text-slate-500 max-w-2xl mx-auto text-lg">Everything you need to bypass desk rejects based on formatting.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: Zap, title: "Instant Generation", desc: "Process 50-page manuscripts in under 3 seconds." },
              { icon: LayoutTemplate, title: "Strict Compliance", desc: "Pixel-perfect margins, fonts, and column layouts for IEEE/ACM." },
              { icon: Shield, title: "100% Secure", desc: "Your pre-published research is deleted immediately after processing." },
              { icon: FileText, title: "Reference Parsing", desc: "Automatically formats citations and reference lists." },
              { icon: CheckCircle2, title: "Figure Extraction", desc: "Intelligently extracts and places figures with captions." },
              { icon: Sparkles, title: "AI Proofing", desc: "Optional AI grammar and academic tone enhancements." }
            ].map((feature, i) => (
              <motion.div 
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="bg-white p-8 rounded-2xl shadow-sm border border-slate-100 hover:shadow-md transition-shadow"
              >
                <div className="w-12 h-12 bg-indigo-50 rounded-xl flex items-center justify-center mb-6">
                  <feature.icon className="w-6 h-6 text-indigo-600" />
                </div>
                <h3 className="text-xl font-semibold text-slate-900 mb-3">{feature.title}</h3>
                <p className="text-slate-500 leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24 px-6 relative overflow-hidden">
        <div className="absolute inset-0 bg-indigo-600"></div>
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Stop Fighting Word Templates.</h2>
          <p className="text-indigo-100 text-lg md:text-xl mb-10 max-w-2xl mx-auto">Join thousands of researchers who have reclaimed their time. Upload your raw document and get a publication-ready DOCX instantly.</p>
          <Link href={user ? "/dashboard" : "/login"} className="px-8 py-4 bg-white text-indigo-600 font-bold rounded-full hover:bg-slate-50 transition-all shadow-xl hover:-translate-y-1 inline-flex items-center">
            Start Formatting for Free
            <ArrowRight className="w-5 h-5 ml-2" />
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-slate-900 py-12 px-6 text-slate-400">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <Sparkles className="w-5 h-5 text-indigo-400" />
            <span className="text-xl font-bold text-white tracking-tight">ManuscriptAI</span>
          </div>
          <div className="flex space-x-6 text-sm">
            <a href="#" className="hover:text-white transition-colors">Privacy Policy</a>
            <a href="#" className="hover:text-white transition-colors">Terms of Service</a>
            <a href="#" className="hover:text-white transition-colors">Contact Support</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
