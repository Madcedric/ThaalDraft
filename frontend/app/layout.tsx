import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/lib/auth-context";
import { ThemeProvider } from "@/components/theme-provider";
import { ErrorBoundary } from "@/components/error-boundary";
import { TooltipProvider } from "@/components/ui/tooltip";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "ThaalDraft — Manuscript Formatter",
  description: "AI-Powered Manuscript Intelligence Platform for academic writing and publication",
  icons: {
    icon: "/favicon.svg",
    shortcut: "/favicon.svg",
    apple: "/logo.png",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}
      suppressHydrationWarning
    >
      <body className="min-h-full flex flex-col">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:z-[100] focus:p-4 focus:bg-primary focus:text-primary-foreground focus:top-0 focus:left-0"
        >
          Skip to main content
        </a>
        <ThemeProvider attribute="class" defaultTheme="light" enableSystem>
          <ErrorBoundary>
            <TooltipProvider>
              <AuthProvider>
                {children}
              </AuthProvider>
            </TooltipProvider>
          </ErrorBoundary>
        </ThemeProvider>
      </body>
    </html>
  );
}
