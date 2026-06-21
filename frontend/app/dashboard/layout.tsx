"use client";

import { ReactNode, useState, useRef, useEffect } from "react";
import {
  LayoutDashboard,
  FileText,
  Settings,
  LogOut,
  ChevronRight,
  Loader2,
  Menu,
  BookOpen,
  Shield,
  MessageSquare,
  Palette,
  Layers,
  Send,
  BarChart3,
  Camera,
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from "next/link";
import { usePathname } from "next/navigation";
import Image from "next/image";

interface NavItem {
  href: string;
  label: string;
  icon: typeof LayoutDashboard;
  disabled?: boolean;
  section?: string;
}

const navItems: NavItem[] = [
  { href: "/dashboard", label: "Workspace", icon: LayoutDashboard, section: "Core" },
  { href: "/dashboard/documents", label: "Documents", icon: FileText, section: "Core" },
  { href: "/dashboard/citations", label: "Citations", icon: BookOpen, section: "Intelligence" },
  { href: "/dashboard/compliance", label: "Compliance", icon: Shield, section: "Intelligence" },
  { href: "/dashboard/reviewer", label: "Reviewer AI", icon: MessageSquare, section: "Production" },
  { href: "/dashboard/formatting", label: "Formatting Studio", icon: Palette, section: "Production" },
  { href: "/dashboard/batch", label: "Batch Processing", icon: Layers, section: "Production" },
  { href: "/dashboard/submission", label: "Submission Package", icon: Send, section: "Production" },
  { href: "/dashboard/reports", label: "Reports", icon: BarChart3, section: "Intelligence" },
  { href: "/dashboard/settings", label: "Settings", icon: Settings, section: "Core" },
];

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, loading, logout } = useAuth();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [profileName, setProfileName] = useState("");
  const fileInputRef = useRef<HTMLInputElement>(null);

  const email = user?.email ?? "";
  const displayName = profileName || user?.displayName || email.split("@")[0] || "User";
  const userInitials = email ? email.substring(0, 2).toUpperCase() : "US";

  useEffect(() => {
    const fetchProfile = async () => {
      if (!user) return;
      try {
        const token = await user.getIdToken();
        const res = await fetch(`${API_BASE}/api/v1/profile`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          if (data.avatar_url) setAvatarUrl(data.avatar_url);
          if (data.display_name) setProfileName(data.display_name);
        }
      } catch {}
    };
    fetchProfile();
  }, [user, pathname]);

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !user) return;
    try {
      const token = await user.getIdToken();
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_BASE}/api/v1/profile/avatar`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });
      if (res.ok) {
        const data = await res.json();
        setAvatarUrl(data.avatar_url);
      }
    } catch (err) {
      console.error("Avatar upload failed:", err);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" aria-label="Loading" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex">
      {/* Desktop Sidebar */}
      <aside className="w-64 bg-[#0F1B33] hidden md:flex flex-col" role="navigation" aria-label="Main navigation">
        <div className="h-16 flex items-center px-5 border-b border-[#1D2C4D]">
          <Link href="/dashboard" className="flex items-center gap-3" aria-label="ThaalDraft Home">
            <Image src="/titleIcon.png" alt="ThaalDraft" width={40} height={40} className="rounded-lg" />
            <span className="text-lg font-bold tracking-tight text-white">ThaalDraft</span>
          </Link>
        </div>

        <nav className="flex-1 px-3 py-4 space-y-1 overflow-y-auto" aria-label="Dashboard navigation">
          <NavContent pathname={pathname} onNavigate={() => {}} />
        </nav>

        <div className="p-3 border-t border-[#1D2C4D] space-y-1">
          <div className="flex items-center justify-between px-3 py-1.5">
            <span className="text-xs font-medium text-white/40">Theme</span>
            <ThemeToggle />
          </div>

          <Link
            href="/dashboard/settings"
            className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-[#1D2C4D] transition-colors"
          >
            <div className="relative group cursor-pointer">
              {avatarUrl || user?.photoURL ? (
                <img src={avatarUrl || user?.photoURL || ""} alt="" className="w-8 h-8 rounded-full object-cover" />
              ) : (
                <div className="w-8 h-8 rounded-full bg-[#D4AF37]/20 flex items-center justify-center text-[#D4AF37] font-semibold text-xs">
                  {userInitials}
                </div>
              )}
              <div className="absolute inset-0 rounded-full bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                <Camera className="w-3.5 h-3.5 text-white" />
              </div>
            </div>
            <div className="min-w-0 flex-1">
              <p className="text-sm font-medium text-white truncate">{displayName}</p>
              <p className="text-xs text-white/50 truncate">{email}</p>
            </div>
          </Link>

          <button
            onClick={logout}
            className="flex items-center w-full px-3 py-2.5 text-white/50 hover:bg-red-500/10 hover:text-red-400 rounded-lg font-medium text-sm transition-colors cursor-pointer"
            aria-label="Sign out of your account"
          >
            <LogOut className="w-5 h-5 mr-3 shrink-0" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-screen overflow-hidden" id="main-content">
        <header className="h-16 flex items-center justify-between px-4 md:px-8 border-b border-border bg-card sticky top-0 z-10" role="banner">
          <div className="flex items-center gap-3">
            <Sheet open={open} onOpenChange={setOpen}>
              <SheetTrigger
                render={
                  <Button variant="ghost" size="icon-sm" className="md:hidden" aria-label="Open navigation menu">
                    <Menu className="w-5 h-5" />
                  </Button>
                }
              />
              <SheetContent side="left" showCloseButton={false} className="w-64 p-0 bg-[#0F1B33]">
                <SheetHeader className="px-5 h-16 flex items-center border-b border-[#1D2C4D]">
                  <SheetTitle className="text-lg font-bold text-white flex items-center gap-3">
                    <Image src="/titleIcon.png" alt="ThaalDraft" width={40} height={40} className="rounded-lg" />
                    ThaalDraft
                  </SheetTitle>
                </SheetHeader>
                <nav className="flex-1 px-3 py-4 space-y-1" aria-label="Mobile navigation">
                  <NavContent pathname={pathname} onNavigate={() => setOpen(false)} />
                </nav>
                <div className="p-3 border-t border-[#1D2C4D] space-y-2">
                  <div className="flex items-center justify-between px-3 py-1.5">
                    <span className="text-xs font-medium text-white/40">Theme</span>
                    <ThemeToggle />
                  </div>
                  <button
                    onClick={() => { logout(); setOpen(false); }}
                    className="flex items-center w-full px-3 py-2.5 text-white/50 hover:bg-red-500/10 hover:text-red-400 rounded-lg font-medium text-sm transition-colors cursor-pointer"
                    aria-label="Sign out"
                  >
                    <LogOut className="w-5 h-5 mr-3 shrink-0" />
                    Sign Out
                  </button>
                </div>
              </SheetContent>
            </Sheet>

            <Link href="/dashboard" className="flex items-center gap-3 md:hidden">
              <Image src="/titleIcon.png" alt="ThaalDraft" width={40} height={40} className="rounded-lg" />
              <span className="text-lg font-bold text-foreground">ThaalDraft</span>
            </Link>

            <h2 className="text-sm font-medium text-muted-foreground hidden md:block">Workspace</h2>
          </div>

          <div className="flex items-center gap-3">
            <ThemeToggle />
            <Link
              href="/dashboard/settings"
              className="w-8 h-8 rounded-full bg-[#D4AF37]/10 border border-[#D4AF37]/20 flex items-center justify-center text-[#D4AF37] font-semibold text-sm hover:bg-[#D4AF37]/20 transition-colors"
              aria-label="Account settings"
            >
              {userInitials}
            </Link>
          </div>
        </header>

        <div className="flex-1 overflow-auto p-4 md:p-8">
          {children}
        </div>
      </main>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        className="hidden"
        onChange={handleAvatarUpload}
      />
    </div>
  );
}

function NavContent({ pathname, onNavigate }: { pathname: string; onNavigate: () => void }) {
  const sections = ["Core", "Intelligence", "Production"];

  return (
    <>
      {sections.map((section) => {
        const sectionItems = navItems.filter((item) => item.section === section);
        if (sectionItems.length === 0) return null;

        return (
          <div key={section} className="mb-4">
            <p className="px-3 py-1.5 text-xs font-semibold text-white/30 uppercase tracking-wider">
              {section}
            </p>
            {sectionItems.map((item) => {
              const isActive = pathname === item.href || (item.href === "/dashboard" && pathname === "/dashboard");

              if (item.disabled) {
                return (
                  <div
                    key={item.href}
                    className="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium text-white/25 cursor-not-allowed"
                    title="Coming in future phase"
                    aria-disabled="true"
                  >
                    <item.icon className="w-5 h-5 mr-3 shrink-0 opacity-50" />
                    {item.label}
                  </div>
                );
              }

              return (
                <Link
                  key={item.href}
                  href={item.href}
                  onClick={onNavigate}
                  className={`flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? "bg-[#D4AF37]/15 text-[#D4AF37]"
                      : "text-white/60 hover:bg-[#1D2C4D] hover:text-white"
                  }`}
                  aria-current={isActive ? "page" : undefined}
                >
                  <item.icon className="w-5 h-5 mr-3 shrink-0" />
                  {item.label}
                  {isActive && <ChevronRight className="w-4 h-4 ml-auto opacity-50" />}
                </Link>
              );
            })}
          </div>
        );
      })}
    </>
  );
}
