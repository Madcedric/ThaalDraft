# Phase 0 — UI Audit

**Audit Date:** June 16, 2026
**Scope:** All frontend pages and components

---

## Current UI Issues

### 1. Landing Page (`app/page.tsx`)

| Issue | Severity | Description |
|---|---|---|
| No mobile menu | HIGH | Navigation links hidden on mobile (`hidden md:flex`) with no hamburger/drawer alternative |
| No SEO metadata | MEDIUM | No Open Graph tags, no structured data, no meta description beyond layout |
| Static feature claims | LOW | "Process 50-page manuscripts in under 3 seconds" — unverified claim, may mislead |
| No loading state for CTA | LOW | "Get Started" button has no loading indicator during auth check |

### 2. Login Page (`app/login/page.tsx`)

| Issue | Severity | Description |
|---|---|---|
| Hardcoded dark background | MEDIUM | `bg-[#0a0a0f]` bypasses design system tokens; should use `bg-background` |
| No password strength indicator | LOW | Only checks `length >= 6`, no visual strength meter |
| No "forgot password" flow | MEDIUM | No password reset mechanism |
| Form inputs not using Shadcn Input | MEDIUM | Uses raw HTML `<input>` instead of `@/components/ui/input` |

### 3. Dashboard Layout (`app/dashboard/layout.tsx`)

| Issue | Severity | Description |
|---|---|---|
| No breadcrumbs | MEDIUM | Deep navigation lacks breadcrumb trail |
| No notification system | MEDIUM | No toast/snackbar for async operation results |
| No user menu dropdown | LOW | User avatar has no dropdown for profile/settings |
| Missing nav items | MEDIUM | Routes to `/dashboard/documents` and `/dashboard/settings` exist in nav but pages don't exist |

### 4. Dashboard Page (`app/dashboard/page.tsx`)

| Issue | Severity | Description |
|---|---|---|
| Only `.docx` upload | HIGH | Accept filter is `.docx` only; PRD requires PDF, LaTeX, Markdown support |
| No drag-and-drop | MEDIUM | Uses file input only; no native drag-and-drop zone |
| No upload progress indicator | MEDIUM | No XHR upload progress; only fake step animation |
| Template list incomplete | MEDIUM | Only IEEE, APA, Nature; PRD requires ACM, Springer, MLA, Elsevier |
| No batch upload | HIGH | Single file only; PRD requires batch processing |
| Fake processing steps | LOW | `setTimeout` animations don't reflect actual backend progress |

### 5. Document Detail Page (`app/dashboard/document/[id]/page.tsx`)

| Issue | Severity | Description |
|---|---|---| 
| Raw UI (no Shadcn) | HIGH | Uses plain HTML (`<div className="p-4 border rounded">`) instead of Card/Alert components |
| No Shadcn tokens | HIGH | Uses `text-slate-500` instead of `text-muted-foreground` |
| `alert()` for feedback | HIGH | Uses browser `alert()` for job enqueue feedback instead of toast/snackbar |
| No error boundary | MEDIUM | No error boundary wrapping; crashes will white-screen |
| No document actions | MEDIUM | No rename, delete, or download actions |
| No status badges | LOW | Status shown as plain text, not colored badges |

### 6. Reports Page (`app/dashboard/reports/page.tsx`)

| Issue | Severity | Description |
|---|---|---| 
| Raw UI (no Shadcn) | HIGH | Uses plain HTML inputs and buttons instead of Shadcn components |
| No Shadcn tokens | HIGH | Uses `text-destructive` but also raw `border rounded px-3 py-2` |
| Manual document ID input | MEDIUM | User must paste document ID; should auto-populate from URL or document list |
| No report visualization | MEDIUM | Shows raw JSON; no charts, progress bars, or human-readable summaries |
| `any` types (3 instances) | LOW | TypeScript lint errors; `reports` state typed as `any[]` |

---

## UX Problems

### Critical

1. **No document list page** — Users cannot see their uploaded documents. The nav links to `/dashboard/documents` but the page doesn't exist.
2. **No settings page** — Nav links to `/dashboard/settings` but page doesn't exist.
3. **No onboarding flow** — New users land on dashboard with no guidance.
4. **No progress feedback** — Upload processing is fake; user has no real visibility into backend job status.

### High

5. **No file type guidance** — Upload zone says `.docx` but PRD promises PDF, LaTeX, Markdown support.
6. **No batch workflow** — PRD requires multi-file upload with queue management; current UI is single-file only.
7. **No export download flow** — After formatting, there's no clear download flow for the generated document.
8. **No document preview** — Users cannot preview parsed content before committing to formatting.

### Medium

9. **No confirmation dialogs** — Destructive actions (delete, overwrite) have no confirmation.
10. **No keyboard shortcuts** — No keyboard navigation or shortcuts for power users.
11. **No search/filter** — No way to search or filter documents or reports.

---

## Accessibility Issues

### Critical

1. **Missing `<main>` landmark** — Landing page has no `<main>` tag; screen readers can't identify primary content.
2. **No skip-to-content link** — No way to skip navigation on any page.
3. **Form labels not associated** — Login page labels use `<label>` but aren't `htmlFor`-linked to inputs.

### High

4. **Color-only status indicators** — Processing steps use color only (green checkmark vs gray dot) without text alternatives.
5. **No `aria-live` regions** — Error messages and status updates aren't announced to screen readers.
6. **Missing `alt` text** — Google SVG icon in login has no `aria-label` or `title`.

### Medium

7. **Focus management** — After form submission errors, focus isn't moved to the error message.
8. **Touch targets** — Mobile nav items may be too small (< 44px tap target).
9. **Contrast ratio** — `text-muted-foreground` on `bg-background` may not meet WCAG AA 4.5:1 ratio.

---

## Summary

| Category | Critical | High | Medium | Low |
|---|---|---|---|---|
| UI Issues | 0 | 4 | 8 | 4 |
| UX Problems | 4 | 4 | 3 | 0 |
| Accessibility | 3 | 3 | 3 | 0 |
| **Total** | **7** | **11** | **14** | **4** |

**Overall Assessment:** The UI has a solid foundation with Shadcn components and design tokens, but significant gaps exist in page coverage (missing document list, settings), mobile experience, and accessibility compliance.
