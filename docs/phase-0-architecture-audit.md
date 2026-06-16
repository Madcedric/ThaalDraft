# Phase 0 — Architecture Audit

**Audit Date:** June 16, 2026
**Scope:** Full-stack folder structure, configuration, and code organization

---

## Folder Structure

### Frontend

```
frontend/
├── app/
│   ├── dashboard/
│   │   ├── document/[id]/page.tsx    (document detail)
│   │   ├── reports/page.tsx          (plagiarism reports)
│   │   ├── layout.tsx                (sidebar + header)
│   │   └── page.tsx                  (upload + format)
│   ├── login/page.tsx                (auth page)
│   ├── globals.css                   (design tokens)
│   ├── layout.tsx                    (root layout)
│   └── page.tsx                      (landing page)
├── components/
│   ├── ui/                           (14 Shadcn components)
│   ├── error-boundary.tsx            (React error boundary)
│   └── skeletons.tsx                 (loading skeletons)
├── lib/
│   ├── auth-context.tsx              (Firebase auth provider)
│   ├── firebase.ts                   (Firebase init)
│   └── utils.ts                      (cn() utility)
├── public/                           (static assets)
├── package.json
├── tsconfig.json
├── next.config.ts
├── components.json                   (Shadcn config)
└── .env / .env.local.example
```

### Backend

```
backend/
├── app/
│   ├── api/routes/
│   │   ├── documents.py              (upload, get, format, jobs)
│   │   ├── auth.py                   (dev login, /me)
│   │   ├── exports.py                (export request, download)
│   │   └── health.py                 (liveness, readiness)
│   ├── models/
│   │   ├── document.py               (Pydantic models)
│   │   └── user.py                   (Pydantic model)
│   ├── services/
│   │   ├── ai_service.py             (OpenAI classification) ⚠️
│   │   ├── auth.py                   (Firebase token verification)
│   │   ├── document_service.py       (Supabase CRUD)
│   │   ├── docx_parser.py            (DOCX parsing)
│   │   ├── export_service.py         (export CRUD)
│   │   ├── format_service.py         (format dispatch)
│   │   ├── ieee_formatter.py         (IEEE DOCX generation)
│   │   ├── job_service.py            (job CRUD)
│   │   ├── pdf_service.py            (DOCX→PDF conversion)
│   │   ├── plagiarism_service.py     (Jaccard similarity)
│   │   ├── storage_service.py        (Supabase Storage)
│   │   ├── struct_service.py         (structure normalization)
│   │   └── user_service.py           (user upsert)
│   └── workers/
│       ├── classify_worker.py        (calls ai_service)
│       ├── format_worker.py          (calls format_service)
│       ├── parse_worker.py           (calls docx_parser)
│       ├── plagiarism_worker.py      (calls plagiarism_service)
│       ├── structure_worker.py       (calls struct_service)
│       └── plagiarism_local_test.py  (manual test script)
├── db/
│   ├── migrations/                   (8 SQL files)
│   ├── README.md
│   └── dbSetup.md
├── uploads/                          (local file storage)
├── requirements.txt
├── requirements_extra.txt
├── .env / .env.example
└── run_worker_with_env.ps1
```

---

## Technical Debt

### Critical

| ID | Location | Issue | Impact |
|---|---|---|---|
| TD-01 | `ai_service.py` | Uses OpenAI API (`gpt-3.5-turbo`) — violates AI policy | Paid API dependency; service dead without API key |
| TD-02 | `requirements.txt` | All AI/ML deps commented out (spacy, transformers, sentence-transformers, torch, chromadb) | Cannot run any NLP/AI features |
| TD-03 | `documents.py:28-33` | `user_id` never set on document creation | Breaks RLS; all user queries fail in production |
| TD-04 | `auth.py:92-98` | Mock tokens accepted without `DEVELOPMENT_MODE` guard | Security risk in production |

### High

| ID | Location | Issue | Impact |
|---|---|---|---|
| TD-05 | `parse_worker.py:36` | `fetch_pending_job()` called without `job_type` filter | Worker could pick up wrong job type |
| TD-06 | `job_service.py:37-58` | Race condition on job pickup (no locking) | Two workers could process same job |
| TD-07 | All workers | `datetime.utcnow()` deprecated in Python 3.12+ | Deprecation warnings; future breakage |
| TD-08 | `plagiarism_service.py` | 5-char shingle Jaccard similarity — toy implementation | Very poor plagiarism detection accuracy |
| TD-09 | `struct_service.py:11-15` | Citation extraction is basic regex only | Misses most citation formats |
| TD-10 | `format_service.py:12` | Only IEEE template supported | PRD requires 6 formats (IEEE, APA, MLA, ACM, Springer, Elsevier) |

### Medium

| ID | Location | Issue | Impact |
|---|---|---|---|
| TD-11 | `main.py:10` | CORS origin hardcoded to `localhost:3000` | Breaks production deployment |
| TD-12 | `health.py:10` | Readiness probe always returns `true` | No real health checking |
| TD-13 | `documents.py:120` | Format endpoint takes synchronous upload | Inconsistent with async job pattern |
| TD-14 | `export_service.py:43-49` | Local fallback scans filesystem | Fragile; doesn't scale |
| TD-15 | `docx_parser.py:33` | Author extraction always returns empty list | Feature incomplete |
| TD-16 | `requirements_extra.txt` | Duplicates `passlib[bcrypt]` and `PyJWT` from main requirements | Confusion about which to install |

---

## Unused Components

### Frontend

| Component | Status | Notes |
|---|---|---|
| `components/ui/avatar.tsx` | Installed, never imported | No page uses Avatar component |
| `components/ui/badge.tsx` | Installed, never imported | Was imported in dashboard/page.tsx but removed |
| `components/ui/dialog.tsx` | Installed, never imported | No confirmation dialogs implemented |
| `components/ui/dropdown-menu.tsx` | Installed, never imported | No user menu dropdown implemented |
| `components/ui/progress.tsx` | Installed, never imported | No progress bars implemented |
| `components/ui/separator.tsx` | Installed, never imported | No horizontal rules implemented |
| `components/ui/tabs.tsx` | Installed, never imported | No tabbed interfaces implemented |

### Backend

| Service | Status | Notes |
|---|---|---|
| `pdf_service.py` | Partially used | Called by `format_worker.py` but has no error handling |
| `storage_service.py` | Partially used | Upload works; download/URL generation is incomplete |
| `user_service.py` | Only called from `/me` endpoint | No other service references it |

---

## Configuration Issues

### Frontend

| File | Issue |
|---|---|
| `.env` | Not in `.gitignore` (only `.env.local` is) |
| `next.config.ts` | Minimal config; no `images` config for external domains |
| `components.json` | `shadcn` CLI tool in `dependencies` instead of `devDependencies` |
| `package.json` | `shadcn` listed as runtime dependency |

### Backend

| File | Issue |
|---|---|
| `.env` | Contains real credentials; not gitignored properly |
| `.env.example` | Lists `OPENAI_API_KEY` (should be `OLLAMA_BASE_URL`) |
| `.env.example` | Duplicate `FIREBASE_PROJECT_ID` entries (lines 7 and 14) |
| `.env.example` | Missing `CORS_ORIGINS`, `DEVELOPMENT_MODE` |
| `requirements.txt` | Uses `>=` without upper bounds; no version pinning strategy |

---

## Missing Infrastructure

| Category | Missing | Notes |
|---|---|---|
| Frontend | `services/` directory | No API service layer; fetch calls scattered in page components |
| Frontend | `hooks/` directory | No custom hooks; auth logic in `lib/auth-context.tsx` |
| Frontend | `types/` directory | Types defined inline in each page component |
| Frontend | `utils/` directory | Only `lib/utils.ts` with `cn()` utility |
| Backend | Task queue (Celery/Redis) | Workers are one-shot scripts with no loop |
| Backend | Structured logging | All logging is `print()` or `console.error()` |
| Backend | Rate limiting | No middleware for API rate limiting |
| Backend | Request validation | Most endpoints accept raw `dict` instead of Pydantic models |
| Backend | Test suite | No pytest, no test files, no CI configuration |
| Backend | API documentation | No OpenAPI security scheme registered |

---

## Summary

| Category | Critical | High | Medium | Low |
|---|---|---|---|---|
| Technical Debt | 4 | 6 | 6 | 0 |
| Unused Components | 0 | 0 | 7 | 0 |
| Configuration Issues | 0 | 0 | 6 | 0 |
| Missing Infrastructure | 0 | 0 | 10 | 0 |
| **Total** | **4** | **6** | **29** | **0** |

**Overall Assessment:** The architecture has a working foundation but significant technical debt around AI policy compliance, missing service layers, and incomplete features. The frontend lacks separation of concerns (no services/hooks/types layers). The backend lacks proper task queuing, logging, and testing infrastructure.
