"use client";

import { useState } from "react";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword,
} from "firebase/auth";
import { auth } from "@/lib/firebase";
import { useAuth } from "@/lib/auth-context";
import { motion, AnimatePresence } from "framer-motion";
import {
  Mail,
  Lock,
  ArrowRight,
  AlertCircle,
  Loader2,
  FileText,
  Brain,
  Zap,
  CheckCircle2,
} from "lucide-react";
import Link from "next/link";
import Image from "next/image";

export default function LoginPage() {
  const [isSignUp, setIsSignUp] = useState(false);
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const { signInWithGoogle } = useAuth();

  const handleAuth = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);

    if (!email || !password) {
      setError("Please fill in all fields.");
      return;
    }

    if (password.length < 6) {
      setError("Password must be at least 6 characters.");
      return;
    }

    if (isSignUp && password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);
    try {
      if (isSignUp) {
        await createUserWithEmailAndPassword(auth, email, password);
      } else {
        await signInWithEmailAndPassword(auth, email, password);
      }
    } catch (err: unknown) {
      const code = (err as { code?: string })?.code ?? null;
      const msg = (err as { message?: string })?.message ?? "";
      const map: Record<string, string> = {
        "auth/invalid-credential": "Incorrect email or password.",
        "auth/wrong-password": "Incorrect email or password.",
        "auth/email-already-in-use": "An account already exists with this email.",
        "auth/invalid-email": "Please enter a valid email address.",
        "auth/weak-password": "Password must be at least 6 characters.",
        "auth/user-not-found": "No account found with this email.",
        "auth/too-many-requests": "Too many attempts. Try again later.",
        "auth/network-request-failed": "Network error. Check your connection.",
      };
      setError(code ? (map[code] ?? `An unexpected error occurred.`) : msg || "An unexpected error occurred.");
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError(null);
    setLoading(true);
    try {
      await signInWithGoogle();
    } catch (err: unknown) {
      const code = (err as { code?: string })?.code ?? "unknown";
      if (code === "auth/popup-closed-by-user") {
        setError(null);
      } else {
        setError(`Google sign-in failed: ${code}`);
      }
      setLoading(false);
    }
  };

  const features = [
    { icon: Brain, label: "AI-Powered Analysis", desc: "Intelligent document review" },
    { icon: FileText, label: "Smart Extraction", desc: "DOCX, PDF, LaTeX parsing" },
    { icon: Zap, label: "Instant Formatting", desc: "7 journal templates" },
  ];

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-[#0F1B33] overflow-hidden">
      {/* Gradient orbs — gold + navy */}
      <div className="absolute top-[-15%] left-[-10%] w-[45%] h-[45%] gradient-orb-1 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-15%] right-[-10%] w-[45%] h-[45%] gradient-orb-2 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute top-[40%] w-[30%] h-[30%] gradient-orb-3 rounded-full blur-[100px] pointer-events-none" />

      <div className="w-full max-w-5xl flex items-center justify-center px-4 py-8 relative z-10 gap-8 lg:gap-16">
        {/* Left: Branding + Features */}
        <motion.div
          initial={{ opacity: 0, x: -30 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="hidden lg:flex flex-col gap-10 max-w-md"
        >
          <Link href="/" className="inline-flex items-center gap-3 mb-8">
            <Image src="/titleIcon.png" alt="ThaalDraft" width={44} height={44} className="rounded-lg" />
            <span className="text-3xl font-bold tracking-tight text-white">ThaalDraft</span>
          </Link>

          <div>
            <h1 className="text-3xl font-bold text-white leading-tight">
              Your manuscript, <span className="text-[#D4AF37]">publication-ready.</span>
            </h1>
            <p className="text-white/50 text-sm leading-relaxed mt-3">
              AI-powered platform that transforms raw drafts into publication-ready papers.
              Format, review, and submit in minutes.
            </p>
          </div>

          <div className="flex flex-col gap-5">
            {features.map((f, i) => (
              <motion.div
                key={f.label}
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.4, delay: 0.3 + i * 0.1 }}
                className="flex items-start gap-3"
              >
                <div className="w-9 h-9 rounded-xl bg-[#D4AF37]/10 flex items-center justify-center shrink-0 mt-0.5">
                  <f.icon className="w-4.5 h-4.5 text-[#D4AF37]" />
                </div>
                <div>
                  <p className="text-sm font-medium text-white">{f.label}</p>
                  <p className="text-xs text-white/40">{f.desc}</p>
                </div>
              </motion.div>
            ))}
          </div>

          <div className="flex items-center gap-2 text-xs text-white/40">
            <CheckCircle2 className="w-3.5 h-3.5 text-[#D4AF37]" />
            <span>Trusted by researchers worldwide</span>
          </div>
        </motion.div>

        {/* Right: Auth Card */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, ease: "easeOut" }}
          className="w-full max-w-md"
        >
          {/* Mobile logo */}
          <div className="lg:hidden flex items-center justify-center gap-3 mb-8">
            <Image src="/titleIcon.png" alt="ThaalDraft" width={44} height={44} className="rounded-lg" />
            <span className="text-3xl font-bold tracking-tight text-white">ThaalDraft</span>
          </div>

          <div className="bg-[#111B2E]/80 backdrop-blur-xl border border-[#1D2C4D] rounded-2xl shadow-2xl">
            <div className="p-8 text-center">
              <h2 className="text-xl font-semibold text-white">
                {isSignUp ? "Create your account" : "Welcome back"}
              </h2>
              <p className="text-sm text-white/40 mt-1">
                {isSignUp ? "Start formatting papers today" : "Sign in to your workspace"}
              </p>
            </div>

            <div className="px-8 pb-8">
              <AnimatePresence mode="wait">
                {error && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mb-4 overflow-hidden"
                  >
                    <div className="flex items-center gap-2 p-3 rounded-xl bg-red-500/10 border border-red-500/20 text-sm text-red-400">
                      <AlertCircle className="w-4 h-4 shrink-0" />
                      {error}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Google Sign-In */}
              <button
                onClick={handleGoogleSignIn}
                disabled={loading}
                className="w-full h-11 border border-[#1D2C4D] bg-[#0F1B33]/50 hover:bg-[#1D2C4D] text-white font-medium rounded-xl flex items-center justify-center gap-2.5 transition-all duration-200 disabled:opacity-50 cursor-pointer mb-5"
              >
                <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                  <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                  <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
                  <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
                </svg>
                Continue with Google
              </button>

              {/* Divider */}
              <div className="flex items-center gap-3 mb-5">
                <div className="flex-1 h-px bg-[#1D2C4D]" />
                <span className="text-xs font-medium text-white/30 uppercase">or</span>
                <div className="flex-1 h-px bg-[#1D2C4D]" />
              </div>

              {/* Form */}
              <form onSubmit={handleAuth} className="space-y-3.5">
                <div>
                  <label className="block text-xs font-medium text-white/50 mb-1.5">Email</label>
                  <div className="relative">
                    <Mail className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                    <input
                      type="email"
                      placeholder="you@example.com"
                      value={email}
                      onChange={(e) => setEmail(e.target.value)}
                      disabled={loading}
                      className="w-full h-11 bg-[#0F1B33]/50 border border-[#1D2C4D] rounded-xl pl-10 pr-4 text-white text-sm placeholder-white/25 focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37]/30 transition-colors disabled:opacity-50"
                      required
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-xs font-medium text-white/50 mb-1.5">Password</label>
                  <div className="relative">
                    <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                    <input
                      type="password"
                      placeholder="Enter password"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      disabled={loading}
                      className="w-full h-11 bg-[#0F1B33]/50 border border-[#1D2C4D] rounded-xl pl-10 pr-4 text-white text-sm placeholder-white/25 focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37]/30 transition-colors disabled:opacity-50"
                      required
                    />
                  </div>
                </div>

                <AnimatePresence>
                  {isSignUp && (
                    <motion.div
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: "auto" }}
                      exit={{ opacity: 0, height: 0 }}
                      className="overflow-hidden"
                    >
                      <label className="block text-xs font-medium text-white/50 mb-1.5">Confirm Password</label>
                      <div className="relative">
                        <Lock className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-white/30" />
                        <input
                          type="password"
                          placeholder="Confirm password"
                          value={confirmPassword}
                          onChange={(e) => setConfirmPassword(e.target.value)}
                          disabled={loading}
                          className="w-full h-11 bg-[#0F1B33]/50 border border-[#1D2C4D] rounded-xl pl-10 pr-4 text-white text-sm placeholder-white/25 focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37]/30 transition-colors disabled:opacity-50"
                          required
                        />
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>

                <button
                  type="submit"
                  disabled={loading}
                  className="w-full h-11 bg-[#D4AF37] hover:bg-[#D4AF37]/90 text-[#0F1B33] font-semibold rounded-xl flex items-center justify-center gap-2 transition-colors disabled:opacity-50 cursor-pointer mt-4 shadow-md shadow-[#D4AF37]/20"
                >
                  {loading ? (
                    <Loader2 className="w-4.5 h-4.5 animate-spin" />
                  ) : (
                    <>
                      {isSignUp ? "Create Account" : "Sign In"}
                      <ArrowRight className="w-4 h-4" />
                    </>
                  )}
                </button>
              </form>

              <div className="mt-5 text-center text-sm text-white/40">
                {isSignUp ? "Already have an account?" : "Don't have an account?"}{" "}
                <button
                  onClick={() => { setIsSignUp(!isSignUp); setError(null); }}
                  className="text-[#D4AF37] hover:text-[#D4AF37]/80 font-semibold cursor-pointer"
                >
                  {isSignUp ? "Sign in" : "Sign up free"}
                </button>
              </div>

              <p className="text-center text-xs text-white/20 mt-5">
                By continuing, you agree to our Terms of Service and Privacy Policy.
              </p>
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
