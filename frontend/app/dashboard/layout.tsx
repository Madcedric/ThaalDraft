"use client";

import { ReactNode } from "react";
import { LayoutDashboard, FileText, Settings, LogOut, ChevronRight, Loader2 } from "lucide-react";
import { useAuth } from "@/lib/auth-context";

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const { user, loading, logout } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-slate-50 flex items-center justify-center">
        <Loader2 className="w-10 h-10 animate-spin text-indigo-600" />
      </div>
    );
  }

  // Get user initials from email
  const userInitials = user?.email
    ? user.email.substring(0, 2).toUpperCase()
    : "US";

  return (
    <div className="min-h-screen bg-slate-50 flex">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-200 bg-white hidden md:flex flex-col">
        <div className="h-16 flex items-center px-6 border-b border-slate-200">
          <span className="text-xl font-bold tracking-tight text-indigo-600">ManuscriptAI</span>
        </div>
        <nav className="flex-1 px-4 py-6 space-y-1">
          <a href="/dashboard" className="flex items-center px-3 py-2.5 bg-indigo-50 text-indigo-600 rounded-lg font-semibold text-sm group">
            <LayoutDashboard className="w-5 h-5 mr-3 text-indigo-600" />
            Dashboard
            <ChevronRight className="w-4 h-4 ml-auto opacity-0 group-hover:opacity-100 transition-opacity" />
          </a>
          <a href="#" className="flex items-center px-3 py-2.5 text-slate-600 hover:bg-slate-50 hover:text-slate-900 rounded-lg font-medium text-sm transition-colors">
            <FileText className="w-5 h-5 mr-3 text-slate-500" />
            My Documents
          </a>
          <a href="#" className="flex items-center px-3 py-2.5 text-slate-600 hover:bg-slate-50 hover:text-slate-900 rounded-lg font-medium text-sm transition-colors">
            <Settings className="w-5 h-5 mr-3 text-slate-500" />
            Settings
          </a>
        </nav>
        <div className="p-4 border-t border-slate-200">
          <button 
            onClick={logout}
            className="flex items-center w-full px-3 py-2 text-slate-600 hover:bg-red-50 hover:text-red-600 rounded-lg font-medium text-sm transition-colors cursor-pointer"
          >
            <LogOut className="w-5 h-5 mr-3" />
            Sign Out
          </button>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-h-screen overflow-hidden">
        {/* Header */}
        <header className="h-16 flex items-center justify-between px-8 border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-10">
          <h2 className="text-lg font-medium text-slate-800">Workspace</h2>
          <div className="flex items-center space-x-4">
            <span className="text-xs text-slate-500 font-medium hidden sm:inline-block">{user?.email}</span>
            <div className="w-8 h-8 rounded-full bg-indigo-100 border border-indigo-200 flex items-center justify-center text-indigo-700 font-semibold text-sm shadow-sm">
              {userInitials}
            </div>
          </div>
        </header>
        
        {/* Scrollable Content */}
        <div className="flex-1 overflow-auto p-8">
          {children}
        </div>
      </main>
    </div>
  );
}
