"use client";

import { useState } from "react";
import {
  signInWithEmailAndPassword,
  createUserWithEmailAndPassword
} from "firebase/auth";
import { auth } from "@/lib/firebase";
import { useAuth } from "@/lib/auth-context";
import { motion, AnimatePresence } from "framer-motion";
import {
  Sparkles,
  Mail,
  Lock,
  ArrowRight,
  AlertCircle,
  Loader2
} from "lucide-react";
import Link from "next/link";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";

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
      console.error("Auth Error:", err);
      const code = (err as { code?: string })?.code ?? null;
      let friendlyMessage = "An unexpected error occurred. Please try again.";

      if (code === "auth/invalid-credential" || code === "auth/wrong-password") {
        friendlyMessage = "Incorrect email or password.";
      } else if (code === "auth/email-already-in-use") {
        friendlyMessage = "An account already exists with this email address.";
      } else if (code === "auth/invalid-email") {
        friendlyMessage = "Please enter a valid email address.";
      } else if (code === "auth/weak-password") {
        friendlyMessage = "Password is too weak. Please use at least 6 characters.";
      } else if (code === "auth/user-not-found") {
        friendlyMessage = "No account found with this email address.";
      } else if (code === "auth/too-many-requests") {
        friendlyMessage = "Too many attempts. Try again later.";
      } else if (code === "auth/network-request-failed") {
        friendlyMessage = "Network error. Check your connection and try again.";
      } else if (code) {
        const msg = (err as { message?: string })?.message ?? "";
        friendlyMessage = `Error: ${code} — ${msg}`;
      }

      setError(friendlyMessage);
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError(null);
    setLoading(true);
    try {
      await signInWithGoogle();
    } catch (err: unknown) {
      console.error("Google Sign-In Error:", err);
      const errObj = err as { code?: string; message?: string };
      if (errObj?.code === "auth/popup-closed-by-user") {
        setError(null);
      } else {
        const code = errObj?.code ?? "unknown_error";
        const message = errObj?.message ?? String(err);
        setError(`Google sign-in failed: ${code} — ${message}`);
      }
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen relative flex items-center justify-center bg-[#0a0a0f] overflow-hidden font-sans">
      <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[50%] bg-primary/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-20%] right-[-10%] w-[50%] h-[50%] bg-purple-900/20 rounded-full blur-[120px] pointer-events-none" />

      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="w-full max-w-md p-8 bg-card/50 backdrop-blur-xl border border-border/50 rounded-3xl shadow-2xl relative z-10 mx-4"
      >
        <div className="flex flex-col items-center space-y-2 mb-8 text-center">
          <Link href="/" className="inline-flex items-center space-x-2 text-primary group">
            <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-300">
              <Sparkles className="w-6 h-6 text-primary-foreground" />
            </div>
            <span className="text-2xl font-bold tracking-tight text-foreground">ThaalDraft</span>
          </Link>
          <p className="text-muted-foreground text-sm font-medium mt-1">
            {isSignUp ? "Create an account to format papers" : "Log in to your workspace"}
          </p>
        </div>

        <AnimatePresence mode="wait">
          {error && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 overflow-hidden"
            >
              <Alert variant="destructive">
                <AlertCircle className="h-4 w-4" />
                <AlertDescription className="text-sm">{error}</AlertDescription>
              </Alert>
            </motion.div>
          )}
        </AnimatePresence>

        <Button
          variant="outline"
          className="w-full h-12 border-border bg-card/50 hover:bg-card text-foreground font-medium rounded-2xl flex items-center justify-center space-x-3 transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed mb-6 shadow-sm cursor-pointer"
          onClick={handleGoogleSignIn}
          disabled={loading}
        >
          <svg className="w-5 h-5 shrink-0" viewBox="0 0 24 24" fill="currentColor">
            <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
            <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
            <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.06H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.94l2.85-2.22.81-.63z" fill="#FBBC05"/>
            <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.06l3.66 2.84c.87-2.6 3.3-4.52 6.16-4.52z" fill="#EA4335"/>
          </svg>
          <span>Continue with Google</span>
        </Button>

        <div className="flex items-center my-6">
          <div className="flex-1 border-t border-border"></div>
          <span className="px-4 text-xs font-semibold uppercase tracking-wider text-muted-foreground">or email</span>
          <div className="flex-1 border-t border-border"></div>
        </div>

        <form onSubmit={handleAuth} className="space-y-4">
          <div>
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Email Address</label>
            <div className="relative">
              <Mail className="absolute left-4 top-3.5 w-5 h-5 text-muted-foreground" />
              <input
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                className="w-full h-12 bg-card/50 border border-border rounded-2xl pl-12 pr-4 text-foreground text-sm placeholder-muted-foreground/50 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors disabled:opacity-50"
                required
              />
            </div>
          </div>

          <div>
            <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Password</label>
            <div className="relative">
              <Lock className="absolute left-4 top-3.5 w-5 h-5 text-muted-foreground" />
              <input
                type="password"
                placeholder="••••••••"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                disabled={loading}
                className="w-full h-12 bg-card/50 border border-border rounded-2xl pl-12 pr-4 text-foreground text-sm placeholder-muted-foreground/50 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors disabled:opacity-50"
                required
              />
            </div>
          </div>

          <AnimatePresence initial={false}>
            {isSignUp && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                exit={{ opacity: 0, height: 0 }}
                className="overflow-hidden"
              >
                <label className="block text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-2">Confirm Password</label>
                <div className="relative">
                  <Lock className="absolute left-4 top-3.5 w-5 h-5 text-muted-foreground" />
                  <input
                    type="password"
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                    disabled={loading}
                    className="w-full h-12 bg-card/50 border border-border rounded-2xl pl-12 pr-4 text-foreground text-sm placeholder-muted-foreground/50 focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-colors disabled:opacity-50"
                    required
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          <Button
            type="submit"
            className="w-full h-12 rounded-2xl flex items-center justify-center space-x-2 transition-colors cursor-pointer shadow-md mt-6"
            disabled={loading}
          >
            {loading ? (
              <Loader2 className="w-5 h-5 animate-spin" />
            ) : (
              <>
                <span>{isSignUp ? "Create Account" : "Log In"}</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-0.5 transition-transform" />
              </>
            )}
          </Button>
        </form>

        <div className="mt-8 text-center text-sm text-muted-foreground font-medium">
          {isSignUp ? (
            <span>
              Already have an account?{" "}
              <button
                onClick={() => { setIsSignUp(false); setError(null); }}
                className="text-primary hover:text-primary/80 font-semibold cursor-pointer underline underline-offset-4"
              >
                Log In
              </button>
            </span>
          ) : (
            <span>
              Don&apos;t have an account?{" "}
              <button
                onClick={() => { setIsSignUp(true); setError(null); }}
                className="text-primary hover:text-primary/80 font-semibold cursor-pointer underline underline-offset-4"
              >
                Sign Up for Free
              </button>
            </span>
          )}
        </div>
      </motion.div>
    </div>
  );
}
