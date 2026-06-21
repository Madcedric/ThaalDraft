"use client";

import { useState, useRef, useEffect } from "react";
import { useAuth } from "@/lib/auth-context";
import { useTheme } from "next-themes";
import {
  User,
  Moon,
  Sun,
  Monitor,
  Bell,
  Shield,
  CreditCard,
  Palette,
  Globe,
  Key,
  LogOut,
  ChevronRight,
  Check,
  Mail,
  Calendar,
  Camera,
  Loader2,
  Save,
} from "lucide-react";

const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

export default function SettingsPage() {
  const { user, logout } = useAuth();
  const { theme, setTheme } = useTheme();
  const [activeTab, setActiveTab] = useState("profile");

  const email = user?.email ?? "";
  const displayName = user?.displayName ?? email.split("@")[0] ?? "User";
  const userInitials = email ? email.substring(0, 2).toUpperCase() : "US";
  const createdDate = user?.metadata?.creationTime
    ? new Date(user.metadata.creationTime).toLocaleDateString("en-US", { month: "long", year: "numeric" })
    : "Unknown";

  const tabs = [
    { id: "profile", label: "Profile", icon: User },
    { id: "appearance", label: "Appearance", icon: Palette },
    { id: "notifications", label: "Notifications", icon: Bell },
    { id: "security", label: "Security", icon: Shield },
    { id: "billing", label: "Billing", icon: CreditCard },
    { id: "api", label: "API Keys", icon: Key },
  ];

  return (
    <div className="max-w-5xl mx-auto">
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-foreground">Settings</h1>
        <p className="text-sm text-muted-foreground mt-1">Manage your account and preferences</p>
      </div>

      <div className="flex flex-col md:flex-row gap-6">
        {/* Sidebar Tabs */}
        <nav className="w-full md:w-56 shrink-0">
          <div className="flex md:flex-col gap-1 overflow-x-auto md:overflow-visible pb-2 md:pb-0">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm font-medium transition-colors whitespace-nowrap cursor-pointer ${
                  activeTab === tab.id
                    ? "bg-[#D4AF37]/10 text-[#D4AF37]"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                }`}
              >
                <tab.icon className="w-4 h-4" />
                {tab.label}
              </button>
            ))}
            <div className="hidden md:block mt-4 pt-4 border-t border-border">
              <button
                onClick={logout}
                className="flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm font-medium text-destructive hover:bg-destructive/10 transition-colors w-full cursor-pointer"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </button>
            </div>
          </div>
        </nav>

        {/* Content */}
        <div className="flex-1 min-w-0">
          {activeTab === "profile" && (
            <ProfileTab user={user} email={email} displayName={displayName} userInitials={userInitials} createdDate={createdDate} />
          )}
          {activeTab === "appearance" && <AppearanceTab theme={theme} setTheme={setTheme} />}
          {activeTab === "notifications" && <NotificationsTab />}
          {activeTab === "security" && <SecurityTab />}
          {activeTab === "billing" && <BillingTab />}
          {activeTab === "api" && <ApiKeysTab />}
        </div>
      </div>
    </div>
  );
}

function ProfileTab({ user, email, displayName, userInitials, createdDate }: {
  user: any; email: string; displayName: string; userInitials: string; createdDate: string;
}) {
  const [name, setName] = useState(displayName);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [avatarUrl, setAvatarUrl] = useState<string | null>(null);
  const [uploading, setUploading] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const fetchProfile = async () => {
      if (!user) return;
      try {
        const token = await user.getIdToken();
        const res = await fetch(`${API_BASE}/api/v1/profile`, { headers: { Authorization: `Bearer ${token}` } });
        if (res.ok) {
          const data = await res.json();
          if (data.avatar_url) setAvatarUrl(data.avatar_url);
          if (data.display_name) setName(data.display_name);
        }
      } catch {}
    };
    fetchProfile();
  }, [user]);

  const handleSave = async () => {
    if (!user) return;
    setSaving(true);
    try {
      const token = await user.getIdToken();
      await fetch(`${API_BASE}/api/v1/profile`, {
        method: "PUT",
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "application/json" },
        body: JSON.stringify({ display_name: name }),
      });
      setSaved(true);
      setTimeout(() => setSaved(false), 2000);
    } catch {}
    setSaving(false);
  };

  const handleAvatarUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file || !user) return;
    setUploading(true);
    try {
      const token = await user.getIdToken();
      const formData = new FormData();
      formData.append("file", file);
      const res = await fetch(`${API_BASE}/api/v1/profile/avatar`, {
        method: "POST", headers: { Authorization: `Bearer ${token}` }, body: formData,
      });
      if (res.ok) { const data = await res.json(); setAvatarUrl(data.avatar_url); }
    } catch {}
    setUploading(false);
  };

  return (
    <div className="space-y-6">
      <div className="bg-card border border-border rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Profile</h2>
        <div className="flex items-center gap-5 mb-6">
          <div className="relative group cursor-pointer" onClick={() => fileInputRef.current?.click()}>
            {avatarUrl ? (
              <img src={avatarUrl} alt="" className="w-16 h-16 rounded-2xl object-cover" />
            ) : (
              <div className="w-16 h-16 rounded-2xl bg-[#D4AF37]/10 border border-[#D4AF37]/20 flex items-center justify-center text-[#D4AF37] font-bold text-xl">
                {userInitials}
              </div>
            )}
            <div className="absolute inset-0 rounded-2xl bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
              {uploading ? <Loader2 className="w-5 h-5 text-white animate-spin" /> : <Camera className="w-5 h-5 text-white" />}
            </div>
            <input ref={fileInputRef} type="file" accept="image/*" className="hidden" onChange={handleAvatarUpload} />
          </div>
          <div>
            <p className="font-semibold text-foreground text-lg">{displayName}</p>
            <p className="text-sm text-muted-foreground">{email}</p>
          </div>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Display Name</label>
            <input type="text" value={name} onChange={(e) => setName(e.target.value)}
              className="w-full h-10 bg-background border border-border rounded-xl px-3.5 text-sm text-foreground focus:outline-none focus:border-[#D4AF37] focus:ring-1 focus:ring-[#D4AF37]/30 transition-colors" />
          </div>
          <div>
            <label className="block text-xs font-medium text-muted-foreground mb-1.5">Email</label>
            <input type="email" value={email} disabled
              className="w-full h-10 bg-muted/50 border border-border rounded-xl px-3.5 text-sm text-muted-foreground cursor-not-allowed" />
          </div>
        </div>
        <div className="flex items-center gap-3 mt-5 text-xs text-muted-foreground">
          <Calendar className="w-3.5 h-3.5" />
          <span>Member since {createdDate}</span>
        </div>
        <div className="mt-5 pt-5 border-t border-border flex justify-end">
          <button onClick={handleSave} disabled={saving}
            className="px-5 py-2 bg-[#D4AF37] text-[#0F1B33] text-sm font-semibold rounded-xl hover:bg-[#D4AF37]/90 transition-colors cursor-pointer shadow-sm shadow-[#D4AF37]/20 flex items-center gap-2 disabled:opacity-50">
            {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : saved ? <Check className="w-4 h-4" /> : <Save className="w-4 h-4" />}
            {saved ? "Saved" : "Save Changes"}
          </button>
        </div>
      </div>
      <div className="bg-card border border-border rounded-2xl p-6">
        <h2 className="text-lg font-semibold text-foreground mb-4">Danger Zone</h2>
        <p className="text-sm text-muted-foreground mb-4">Permanently delete your account and all associated data.</p>
        <button className="px-5 py-2 border border-destructive/30 text-destructive text-sm font-medium rounded-xl hover:bg-destructive/10 transition-colors cursor-pointer">
          Delete Account
        </button>
      </div>
    </div>
  );
}

function AppearanceTab({ theme, setTheme }: { theme: string | undefined; setTheme: (t: string) => void }) {
  const themes = [
    { id: "light", label: "Light", icon: Sun, desc: "Bright and clean" },
    { id: "dark", label: "Dark", icon: Moon, desc: "Navy dark mode" },
    { id: "system", label: "System", icon: Monitor, desc: "Match your OS" },
  ];

  return (
    <div className="bg-card border border-border rounded-2xl p-6">
      <h2 className="text-lg font-semibold text-foreground mb-1">Appearance</h2>
      <p className="text-sm text-muted-foreground mb-5">Customize how ThaalDraft looks on your device.</p>
      <div className="grid grid-cols-3 gap-3">
        {themes.map((t) => (
          <button key={t.id} onClick={() => setTheme(t.id)}
            className={`relative flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all cursor-pointer ${
              theme === t.id ? "border-[#D4AF37] bg-[#D4AF37]/5" : "border-border hover:border-border/80 hover:bg-muted/50"
            }`}>
            {theme === t.id && (
              <div className="absolute top-2 right-2 w-5 h-5 bg-[#D4AF37] rounded-full flex items-center justify-center">
                <Check className="w-3 h-3 text-[#0F1B33]" />
              </div>
            )}
            <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${
              theme === t.id ? "bg-[#D4AF37]/10 text-[#D4AF37]" : "bg-muted text-muted-foreground"
            }`}>
              <t.icon className="w-5 h-5" />
            </div>
            <div className="text-center">
              <p className="text-sm font-medium text-foreground">{t.label}</p>
              <p className="text-xs text-muted-foreground">{t.desc}</p>
            </div>
          </button>
        ))}
      </div>
    </div>
  );
}

function NotificationsTab() {
  const settings = [
    { label: "Email notifications", desc: "Receive updates about your documents", enabled: true },
    { label: "Processing alerts", desc: "Get notified when jobs complete", enabled: true },
    { label: "Weekly digest", desc: "Summary of your activity", enabled: false },
    { label: "Product updates", desc: "New features and improvements", enabled: true },
  ];
  return (
    <div className="bg-card border border-border rounded-2xl p-6">
      <h2 className="text-lg font-semibold text-foreground mb-1">Notifications</h2>
      <p className="text-sm text-muted-foreground mb-5">Choose what notifications you receive.</p>
      <div className="space-y-4">
        {settings.map((s) => (
          <div key={s.label} className="flex items-center justify-between py-2">
            <div>
              <p className="text-sm font-medium text-foreground">{s.label}</p>
              <p className="text-xs text-muted-foreground">{s.desc}</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input type="checkbox" defaultChecked={s.enabled} className="sr-only peer" />
              <div className="w-9 h-5 bg-muted peer-focus:ring-2 peer-focus:ring-[#D4AF37]/30 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#D4AF37]"></div>
            </label>
          </div>
        ))}
      </div>
    </div>
  );
}

function SecurityTab() {
  return (
    <div className="bg-card border border-border rounded-2xl p-6">
      <h2 className="text-lg font-semibold text-foreground mb-1">Security</h2>
      <p className="text-sm text-muted-foreground mb-5">Manage your account security settings.</p>
      <div className="space-y-4">
        <div className="flex items-center justify-between py-3 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-emerald-500/10 flex items-center justify-center">
              <Shield className="w-4 h-4 text-emerald-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Two-Factor Authentication</p>
              <p className="text-xs text-muted-foreground">Add an extra layer of security</p>
            </div>
          </div>
          <button className="px-3.5 py-1.5 text-xs font-medium text-[#D4AF37] border border-[#D4AF37]/30 rounded-lg hover:bg-[#D4AF37]/5 transition-colors cursor-pointer">Enable</button>
        </div>
        <div className="flex items-center justify-between py-3 border-b border-border">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-[#D4AF37]/10 flex items-center justify-center">
              <Key className="w-4 h-4 text-[#D4AF37]" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Change Password</p>
              <p className="text-xs text-muted-foreground">Update your password regularly</p>
            </div>
          </div>
          <button className="px-3.5 py-1.5 text-xs font-medium text-[#D4AF37] border border-[#D4AF37]/30 rounded-lg hover:bg-[#D4AF37]/5 transition-colors cursor-pointer">Update</button>
        </div>
        <div className="flex items-center justify-between py-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-blue-500/10 flex items-center justify-center">
              <Globe className="w-4 h-4 text-blue-500" />
            </div>
            <div>
              <p className="text-sm font-medium text-foreground">Active Sessions</p>
              <p className="text-xs text-muted-foreground">Manage devices signed into your account</p>
            </div>
          </div>
          <button className="px-3.5 py-1.5 text-xs font-medium text-muted-foreground border border-border rounded-lg hover:bg-muted transition-colors cursor-pointer">View All</button>
        </div>
      </div>
    </div>
  );
}

function BillingTab() {
  return (
    <div className="bg-card border border-border rounded-2xl p-6">
      <h2 className="text-lg font-semibold text-foreground mb-1">Billing</h2>
      <p className="text-sm text-muted-foreground mb-5">Manage your subscription and payment method.</p>
      <div className="bg-[#D4AF37]/5 border border-[#D4AF37]/20 rounded-xl p-5 mb-5">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-semibold text-foreground">Free Plan</p>
            <p className="text-sm text-muted-foreground mt-0.5">5 documents per month</p>
          </div>
          <button className="px-4 py-2 bg-[#D4AF37] text-[#0F1B33] text-sm font-semibold rounded-xl hover:bg-[#D4AF37]/90 transition-colors cursor-pointer shadow-sm shadow-[#D4AF37]/20">
            Upgrade to Pro
          </button>
        </div>
        <div className="mt-4 flex items-center gap-6 text-xs text-muted-foreground">
          <span>Documents used: <span className="font-medium text-foreground">2 / 5</span></span>
          <span>Resets in <span className="font-medium text-foreground">12 days</span></span>
        </div>
        <div className="mt-3 w-full h-1.5 bg-muted rounded-full overflow-hidden">
          <div className="h-full bg-[#D4AF37] rounded-full" style={{ width: "40%" }} />
        </div>
      </div>
      <div className="space-y-3">
        <div className="flex items-center justify-between py-3 border-b border-border">
          <div className="flex items-center gap-3">
            <CreditCard className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-foreground">Payment Method</span>
          </div>
          <button className="text-xs text-[#D4AF37] hover:text-[#D4AF37]/80 font-medium cursor-pointer">Add</button>
        </div>
        <div className="flex items-center justify-between py-3">
          <div className="flex items-center gap-3">
            <Mail className="w-4 h-4 text-muted-foreground" />
            <span className="text-sm text-foreground">Invoice History</span>
          </div>
          <ChevronRight className="w-4 h-4 text-muted-foreground" />
        </div>
      </div>
    </div>
  );
}

function ApiKeysTab() {
  return (
    <div className="bg-card border border-border rounded-2xl p-6">
      <h2 className="text-lg font-semibold text-foreground mb-1">API Keys</h2>
      <p className="text-sm text-muted-foreground mb-5">Manage API keys for programmatic access.</p>
      <div className="border border-dashed border-border rounded-xl p-8 text-center">
        <Key className="w-8 h-8 text-muted-foreground/50 mx-auto mb-3" />
        <p className="text-sm font-medium text-foreground mb-1">No API keys yet</p>
        <p className="text-xs text-muted-foreground mb-4">Create an API key to access ThaalDraft programmatically.</p>
        <button className="px-4 py-2 bg-[#D4AF37] text-[#0F1B33] text-sm font-semibold rounded-xl hover:bg-[#D4AF37]/90 transition-colors cursor-pointer shadow-sm shadow-[#D4AF37]/20">
          Create API Key
        </button>
      </div>
    </div>
  );
}
