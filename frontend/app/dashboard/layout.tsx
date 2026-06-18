"use client";

import { ReactNode, useState } from "react";
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
} from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import Link from "next/link";
import { usePathname } from "next/navigation";

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
  { href: "/dashboard/reviewer", label: "Reviewer AI", icon: MessageSquare, disabled: true, section: "Production" },
  { href: "/dashboard/formatting", label: "Formatting Studio", icon: Palette, disabled: true, section: "Production" },
  { href: "/dashboard/batch", label: "Batch Processing", icon: Layers, disabled: true, section: "Production" },
  { href: "/dashboard/settings", label: "Settings", icon: Settings, section: "Core" },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, loading, logout } = useAuth();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  const email = user?.email ?? "";
  const userInitials = email ? email.substring(0, 2).toUpperCase() : "US";

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
      <aside className="w-64 border-r border-border bg-card hidden md:flex flex-col" role="navigation" aria-label="Main navigation">
        <div className="h-14 flex items-center px-6 border-b border-border">
          <Link href="/dashboard" className="text-lg font-bold tracking-tight text-primary" aria-label="ThaalDraft Home">
            ThaalDraft
          </Link>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1" aria-label="Dashboard navigation">
          <NavContent pathname={pathname} onNavigate={() => {}} />
        </nav>
        <div className="p-3 border-t border-border">
          <button
            onClick={logout}
            className="flex items-center w-full px-3 py-2.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive rounded-lg font-medium text-sm transition-colors cursor-pointer"
            aria-label="Sign out of your account"
          >
            <LogOut className="w-5 h-5 mr-3 shrink-0" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-screen overflow-hidden" id="main-content">
        {/* Header */}
        <header className="h-14 flex items-center justify-between px-4 md:px-8 border-b border-border bg-card/80 backdrop-blur-md sticky top-0 z-10" role="banner">
          <div className="flex items-center gap-3">
            {/* Mobile menu trigger */}
            <Sheet open={open} onOpenChange={setOpen}>
              <SheetTrigger
                render={
                  <Button variant="ghost" size="icon-sm" className="md:hidden" aria-label="Open navigation menu">
                    <Menu className="w-5 h-5" />
                  </Button>
                }
              />
              <SheetContent side="left" showCloseButton={false} className="w-64 p-0 bg-card">
                <SheetHeader className="px-6 h-14 flex items-center border-b border-border">
                  <SheetTitle className="text-lg font-bold text-primary">ThaalDraft</SheetTitle>
                </SheetHeader>
                <nav className="flex-1 px-3 py-4 space-y-1" aria-label="Mobile navigation">
                  <NavContent pathname={pathname} onNavigate={() => setOpen(false)} />
                </nav>
                <div className="p-3 border-t border-border">
                  <button
                    onClick={() => { logout(); setOpen(false); }}
                    className="flex items-center w-full px-3 py-2.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive rounded-lg font-medium text-sm transition-colors cursor-pointer"
                    aria-label="Sign out"
                  >
                    <LogOut className="w-5 h-5 mr-3 shrink-0" />
                    Sign Out
                  </button>
                </div>
              </SheetContent>
            </Sheet>
            <Link href="/dashboard" className="text-lg font-bold tracking-tight text-primary md:hidden" aria-label="ThaalDraft Home">
              ThaalDraft
            </Link>
            <h2 className="text-sm font-medium text-muted-foreground hidden md:block">Workspace</h2>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground font-medium hidden sm:inline-block">{user?.email}</span>
            <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-semibold text-sm" aria-label={`User: ${email}`}>
              {userInitials}
            </div>
          </div>
        </header>
        
        {/* Scrollable Content */}
        <div className="flex-1 overflow-auto p-4 md:p-8">
          {children}
        </div>
      </main>
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
            <p className="px-3 py-1.5 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              {section}
            </p>
            {sectionItems.map((item) => {
              const isActive = pathname === item.href || (item.href === "/dashboard" && pathname === "/dashboard");
              
              if (item.disabled) {
                return (
                  <div
                    key={item.href}
                    className="flex items-center px-3 py-2.5 rounded-lg text-sm font-medium text-muted-foreground/50 cursor-not-allowed"
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
                      ? "bg-primary/10 text-primary"
                      : "text-muted-foreground hover:bg-muted hover:text-foreground"
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
