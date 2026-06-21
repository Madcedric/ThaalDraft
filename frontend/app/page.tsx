"use client";

import { motion } from "framer-motion";
import { ArrowRight, CheckCircle2, FileText, Zap, Shield, LayoutTemplate, UploadCloud } from "lucide-react";
import Link from "next/link";
import Image from "next/image";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";

export default function LandingPage() {
  const { user, loading } = useAuth();

  return (
    <div className="min-h-screen bg-background selection:bg-[#D4AF37]/20 selection:text-[#0F1B33]">

      {/* Navigation — Navy */}
      <nav className="fixed top-0 w-full bg-[#0F1B33]/95 backdrop-blur-md border-b border-[#1D2C4D] z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <Image src="/titleIcon.png" alt="ThaalDraft" width={44} height={44} className="rounded-lg" />
            <span className="text-xl font-bold text-white tracking-tight">ThaalDraft</span>
          </div>
          <div className="hidden md:flex space-x-8">
            <a href="#features" className="text-sm font-medium text-white/50 hover:text-[#D4AF37] transition-colors">Features</a>
            <a href="#demo" className="text-sm font-medium text-white/50 hover:text-[#D4AF37] transition-colors">How it Works</a>
          </div>
          <div className="flex items-center space-x-4">
            {loading ? (
              <div className="h-9 w-24 bg-white/10 rounded-full animate-pulse" />
            ) : user ? (
              <Link href="/dashboard">
                <Button size="sm" className="rounded-full bg-[#D4AF37] text-[#0F1B33] hover:bg-[#D4AF37]/90 font-semibold">Go to Dashboard</Button>
              </Link>
            ) : (
              <>
                <Link href="/login" className="hidden sm:block text-sm font-medium text-white/50 hover:text-[#D4AF37] transition-colors">Log in</Link>
                <Link href="/login">
                  <Button size="sm" className="rounded-full bg-[#D4AF37] text-[#0F1B33] hover:bg-[#D4AF37]/90 font-semibold">Get Started</Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section — Navy */}
      <section className="pt-32 pb-20 px-6 bg-[#0F1B33] relative overflow-hidden">
        <div className="absolute top-[-20%] right-[-10%] w-[40%] h-[40%] bg-[#D4AF37] opacity-[0.04] rounded-full blur-[120px] pointer-events-none" />
        <div className="absolute bottom-[-20%] left-[-10%] w-[40%] h-[40%] bg-[#1D2C4D] opacity-50 rounded-full blur-[120px] pointer-events-none" />

        <div className="max-w-7xl mx-auto text-center space-y-8 relative z-10">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="inline-flex items-center space-x-2 px-3 py-1 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/20 text-[#D4AF37] text-sm font-medium mb-4"
          >
            <span>ThaalDraftEngine 2.0 Live</span>
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold text-white tracking-tight max-w-4xl mx-auto leading-[1.1]"
          >
            Publish Faster. <span className="text-[#D4AF37]">Format Smarter.</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.2 }}
            className="text-lg md:text-xl text-white/50 max-w-2xl mx-auto"
          >
            Instantly convert your raw DOCX manuscripts into publication-ready IEEE, ACM, and Springer formats using intelligent AI automation.
          </motion.p>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5, delay: 0.3 }}
            className="flex flex-col sm:flex-row items-center justify-center gap-4 pt-4"
          >
            <Link href={user ? "/dashboard" : "/login"} className="w-full sm:w-auto">
              <Button size="lg" className="w-full sm:w-auto px-8 py-6 text-base rounded-full bg-[#D4AF37] text-[#0F1B33] hover:bg-[#D4AF37]/90 font-semibold shadow-lg shadow-[#D4AF37]/20 hover:shadow-xl hover:-translate-y-0.5 group">
                Convert to IEEE / ACM
                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
              </Button>
            </Link>
            <Link href="#demo" className="w-full sm:w-auto">
              <Button variant="outline" size="lg" className="w-full sm:w-auto px-8 py-6 text-base rounded-full border-[#1D2C4D] text-white/70 hover:bg-[#1D2C4D] hover:text-white">
                View Demo
              </Button>
            </Link>
          </motion.div>
        </div>
      </section>

      {/* Upload Preview */}
      <section className="pb-24 px-6 relative z-10 -mt-8 bg-[#0F1B33] hidden md:block">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.4 }}
          className="max-w-4xl mx-auto bg-[#111B2E] rounded-2xl shadow-2xl border border-[#1D2C4D] overflow-hidden"
        >
          <div className="bg-[#0B1120] border-b border-[#1D2C4D] p-4 flex items-center space-x-2">
            <div className="w-3 h-3 rounded-full bg-red-400"></div>
            <div className="w-3 h-3 rounded-full bg-amber-400"></div>
            <div className="w-3 h-3 rounded-full bg-green-400"></div>
          </div>
          <Link href={user ? "/dashboard" : "/login"} className="block p-12 border-2 border-dashed border-[#D4AF37]/20 mx-8 my-8 rounded-xl bg-[#D4AF37]/5 flex flex-col items-center justify-center text-center group hover:border-[#D4AF37]/40 hover:bg-[#D4AF37]/10 transition-colors cursor-pointer">
            <div className="w-16 h-16 bg-[#0F1B33] rounded-full shadow-sm flex items-center justify-center mb-6 group-hover:scale-110 transition-transform duration-300 border border-[#1D2C4D]">
              <UploadCloud className="w-8 h-8 text-[#D4AF37]" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Drag your manuscript here</h3>
            <p className="text-white/40 max-w-sm">We&apos;ll automatically detect headings, citations, and structure to generate a perfectly formatted academic paper.</p>
          </Link>
        </motion.div>
      </section>

      {/* Before / After */}
      <section id="demo" className="py-24 bg-card px-6 border-t border-border">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">From Draft to Camera-Ready</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto text-lg">See the intelligence in action. We transform unstructured text into strictly compliant journal formats.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-8 items-center max-w-5xl mx-auto">
            <div className="bg-muted rounded-2xl p-8 border border-border relative h-72">
              <div className="absolute top-4 right-4 bg-[#1D2C4D] text-white text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">Before</div>
              <div className="font-mono text-sm text-muted-foreground space-y-4 opacity-70 pt-8">
                <p className="font-bold text-lg text-foreground">AI in Healthcare: A Comprehensive Review</p>
                <p>abstract: This paper explores the integration of artificial intelligence in modern clinical settings...</p>
                <p className="uppercase mt-6 text-foreground">Introduction</p>
                <p>Recently there has been a surge in machine learning applications...</p>
              </div>
            </div>
            <div className="bg-[#D4AF37]/5 rounded-2xl p-8 border border-[#D4AF37]/10 relative shadow-inner h-72">
              <div className="absolute top-4 right-4 bg-[#D4AF37] text-[#0F1B33] text-xs font-bold px-3 py-1 rounded-full uppercase tracking-wider">After (IEEE)</div>
              <div className="font-serif text-sm text-foreground flex flex-col items-center text-center space-y-4 pt-8">
                <h1 className="text-xl font-bold">AI in Healthcare: A Comprehensive Review</h1>
                <p className="italic text-xs px-8 text-justify text-muted-foreground">Abstract—This paper explores the integration of artificial intelligence in modern clinical settings...</p>
                <h2 className="text-sm font-bold uppercase tracking-widest mt-4">I. Introduction</h2>
                <p className="text-left text-xs leading-relaxed text-justify indent-4 w-full px-8 text-muted-foreground">Recently there has been a surge in machine learning applications...</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Grid */}
      <section id="features" className="py-24 px-6 bg-background">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold text-foreground mb-4">Built for Academics</h2>
            <p className="text-muted-foreground max-w-2xl mx-auto text-lg">Everything you need to bypass desk rejects based on formatting.</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              { icon: Zap, title: "Instant Generation", desc: "Process 50-page manuscripts in under 3 seconds." },
              { icon: LayoutTemplate, title: "Strict Compliance", desc: "Pixel-perfect margins, fonts, and column layouts for IEEE/ACM." },
              { icon: Shield, title: "100% Secure", desc: "Your pre-published research is deleted immediately after processing." },
              { icon: FileText, title: "Reference Parsing", desc: "Automatically formats citations and reference lists." },
              { icon: CheckCircle2, title: "Figure Extraction", desc: "Intelligently extracts and places figures with captions." },
              { icon: UploadCloud, title: "AI Proofing", desc: "Optional AI grammar and academic tone enhancements." }
            ].map((feature, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: i * 0.1 }}
                className="bg-card p-8 rounded-2xl shadow-sm border border-border hover:shadow-md transition-shadow"
              >
                <div className="w-12 h-12 bg-[#D4AF37]/10 rounded-xl flex items-center justify-center mb-6">
                  <feature.icon className="w-6 h-6 text-[#D4AF37]" />
                </div>
                <h3 className="text-xl font-semibold text-foreground mb-3">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.desc}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA — Navy */}
      <section className="py-24 px-6 relative overflow-hidden bg-[#0F1B33]">
        <div className="absolute inset-0 bg-[#D4AF37] opacity-[0.03]" />
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h2 className="text-3xl md:text-5xl font-bold text-white mb-6">Stop Fighting Word Templates.</h2>
          <p className="text-white/50 text-lg md:text-xl mb-10 max-w-2xl mx-auto">Join thousands of researchers who have reclaimed their time. Upload your raw document and get a publication-ready DOCX instantly.</p>
          <Link href={user ? "/dashboard" : "/login"}>
            <Button size="lg" className="px-8 py-6 text-base font-bold rounded-full bg-[#D4AF37] text-[#0F1B33] hover:bg-[#D4AF37]/90 shadow-xl shadow-[#D4AF37]/20 hover:-translate-y-1 inline-flex items-center">
              Start Formatting for Free
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer — Navy */}
      <footer className="bg-[#0B1120] py-12 px-6 border-t border-[#1D2C4D]">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between">
          <div className="flex items-center gap-3 mb-4 md:mb-0">
            <Image src="/titleIcon.png" alt="ThaalDraft" width={28} height={28} className="rounded-lg" />
            <span className="text-xl font-bold text-white tracking-tight">ThaalDraft</span>
          </div>
          <div className="flex space-x-6 text-sm">
            <a href="#" className="text-white/40 hover:text-[#D4AF37] transition-colors">Privacy Policy</a>
            <a href="#" className="text-white/40 hover:text-[#D4AF37] transition-colors">Terms of Service</a>
            <a href="#" className="text-white/40 hover:text-[#D4AF37] transition-colors">Contact Support</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
