"use client";

import { ReactNode, useState } from "react";
import { LayoutDashboard, FileText, Settings, LogOut, ChevronRight, Loader2, Menu } from "lucide-react";
import { useAuth } from "@/lib/auth-context";
import { Button } from "@/components/ui/button";
import { Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle } from "@/components/ui/sheet";
import Link from "next/link";
import { usePathname } from "next/navigation";

const navItems = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/dashboard/documents", label: "My Documents", icon: FileText },
  { href: "/dashboard/settings", label: "Settings", icon: Settings },
];

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, loading, logout } = useAuth();
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  if (loading) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  const userInitials = user?.email
    ? user.email.substring(0, 2).toUpperCase()
    : "US";

  function NavContent() {
    return (
      <>
        {navItems.map((item) => {
          const isActive = pathname === item.href || (item.href === "/dashboard" && pathname === "/dashboard");
          return (
            <Link
              key={item.href}
              href={item.href}
              onClick={() => setOpen(false)}
              className={`flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-muted hover:text-foreground"
              }`}
            >
              <item.icon className="w-5 h-5 mr-3 shrink-0" />
              {item.label}
              {isActive && <ChevronRight className="w-4 h-4 ml-auto opacity-50" />}
            </Link>
          );
        })}
      </>
    );
  }

  return (
    <div className="min-h-screen bg-background flex">
      {/* Desktop Sidebar */}
      <aside className="w-64 border-r border-border bg-card hidden md:flex flex-col">
        <div className="h-14 flex items-center px-6 border-b border-border">
          <Link href="/dashboard" className="text-lg font-bold tracking-tight text-primary">
            ThaalDraft
          </Link>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          <NavContent />
        </nav>
        <div className="p-3 border-t border-border">
          <button
            onClick={logout}
            className="flex items-center w-full px-3 py-2.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive rounded-lg font-medium text-sm transition-colors cursor-pointer"
          >
            <LogOut className="w-5 h-5 mr-3 shrink-0" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-screen overflow-hidden">
        {/* Header */}
        <header className="h-14 flex items-center justify-between px-4 md:px-8 border-b border-border bg-card/80 backdrop-blur-md sticky top-0 z-10">
          <div className="flex items-center gap-3">
            {/* Mobile menu trigger */}
            <Sheet open={open} onOpenChange={setOpen}>
              <SheetTrigger
                render={
                  <Button variant="ghost" size="icon-sm" className="md:hidden">
                    <Menu className="w-5 h-5" />
                    <span className="sr-only">Open menu</span>
                  </Button>
                }
              />
              <SheetContent side="left" showCloseButton={false} className="w-64 p-0 bg-card">
                <SheetHeader className="px-6 h-14 flex items-center border-b border-border">
                  <SheetTitle className="text-lg font-bold text-primary">ThaalDraft</SheetTitle>
                </SheetHeader>
                <nav className="flex-1 px-3 py-4 space-y-1">
                  <NavContent />
                </nav>
                <div className="p-3 border-t border-border">
                  <button
                    onClick={() => { logout(); setOpen(false); }}
                    className="flex items-center w-full px-3 py-2.5 text-muted-foreground hover:bg-destructive/10 hover:text-destructive rounded-lg font-medium text-sm transition-colors cursor-pointer"
                  >
                    <LogOut className="w-5 h-5 mr-3 shrink-0" />
                    Sign Out
                  </button>
                </div>
              </SheetContent>
            </Sheet>
            <Link href="/dashboard" className="text-lg font-bold tracking-tight text-primary md:hidden">
              ThaalDraft
            </Link>
            <h2 className="text-sm font-medium text-muted-foreground hidden md:block">Workspace</h2>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-muted-foreground font-medium hidden sm:inline-block">{user?.email}</span>
            <div className="w-8 h-8 rounded-full bg-primary/10 border border-primary/20 flex items-center justify-center text-primary font-semibold text-sm">
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
