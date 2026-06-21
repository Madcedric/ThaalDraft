# ThaalDraft — Project Status

**Generated:** 2026-06-19
**Audit Method:** Codebase inspection + Git history + Existing reports

---

## Project Overview

| Area | Maturity |
|------|----------|
| **Architecture** | 85% |
| **Backend** | 80% |
| **Frontend** | 65% |
| **Database** | 75% |
| **Integration** | 70% |
| **Overall** | **75%** |

---

## Phase Status

### Phase 0 — Architecture Audit

**Status:** Complete

**Implemented:**
- Full architecture audit report
- UI audit
- Database audit
- Refactoring roadmap

**Evidence:**
- `SYSTEM_AUDIT.md`, `SYSTEM_AUDIT_REPORT.md`, `SYSTEM_VALIDATION_REPORT.md`
- Git commit `d9d232f`, `79c65ce`

---

### Phase 1 — Architecture Refactor

**Status:** Complete

**Implemented:**
- Clean folder structure (`services/`, `types/`, `hooks/`, `utils/`, `components/`)
- Shadcn UI token system
- Error boundary components
- Skeleton loading states
- Mobile navigation
- Centralized `api.ts` service layer

**Evidence:**
- `frontend/services/api.ts`
- `frontend/hooks/use-upload.ts`, `use-document.ts`
- `frontend/types/index.ts` (433 lines, 25+ interfaces)
- Git commit `d9d232f`, `cfb6172`

---

### Phase 2 — Document Processing Engine

**Status:** Complete (backend) / Working (frontend)

**Implemented:**
- DOCX parser (`python-docx`)
- PDF parser (`PyMuPDF`)
- LaTeX parser (`pylatexenc`)
- Markdown parser (regex-based)
- Upload API (`POST /upload`)
- Synchronous parse API (`POST /parse`)
- File validation (size, type)
- Metatada extraction
- Local file storage with Supabase Storage integration

**Evidence:**
- `backend/app/services/document_parser.py`
- `backend/app/services/docx_parser.py`
- `backend/app/services/pdf_parser.py`
- `backend/app/services/latex_parser.py`
- `backend/app/services/markdown_parser.py`
- `backend/app/services/storage_service.py`
- `backend/app/api/routes/documents.py` (endpoints: upload, parse, get, list, delete)

---

### Phase 3 — Structure Intelligence Engine

**Status:** Complete (backend, deterministic) / Partial (frontend)

**Implemented:**
- Section classifier (deterministic regex-based, no spaCy/SciBERT used)
- Metadata extraction
- Structure validation
- Confidence reporting
- Backward compatibility layer
- Structure analysis API (`POST /{id}/analyze`, `GET /{id}/structure`)
- Frontend document detail page with section display

**Evidence:**
- `backend/app/services/structure/` (classifier.py, metadata_extractor.py, validator.py, schema.py, rules.py)
- `backend/app/services/struct_service.py`
- `backend/app/api/routes/documents.py` (analyze, structure endpoints)
- `frontend/app/dashboard/document/[id]/page.tsx`

**Note:** spaCy and SciBERT are commented out in `requirements.txt`. The classifier currently uses pattern matching only. NLP models not integrated.

---

### Phase 4 — Citation Intelligence Engine

**Status:** Complete (backend) / Partial (frontend)

**Implemented:**
- Citation extraction (13 regex patterns, numeric + author-year + LaTeX)
- Reference validation (orphan, broken, duplicate detection)
- DOI resolution (CrossRef + OpenAlex APIs)
- Citation health score (composite: 5 dimensions)
- Citation style detection
- 3 API endpoints (analyze, get report, get health)
- Background worker for async processing
- Frontend citations page (metrics + document list)

**Evidence:**
- `backend/app/services/citation/` (analyzer.py, extractor.py, validator.py, resolver.py, rules.py, schema.py)
- `backend/app/api/routes/citations.py`
- `backend/app/workers/citation_worker.py`
- `frontend/app/dashboard/citations/page.tsx`

**Note:** Semantic Scholar integration not wired (no API key). Frontend reads `structured_json` instead of calling citation endpoints directly.

---

### Phase 5 — Journal Compliance Engine

**Status:** Complete (backend) / Partial (frontend)

**Implemented:**
- Rule definitions for 7 journals (IEEE, ACM, Springer, Elsevier, APA, MLA, Nature)
- 9 compliance checks (word count, abstract length, reference count, citation style, figure limit, section structure, keyword count, title length, DOI required)
- Compliance score computation
- 4 API endpoints (list journals, get journal, analyze, get report)
- Frontend compliance page (metrics + journal selector)

**Evidence:**
- `backend/app/services/compliance/` (analyzer.py, rules.py, schema.py)
- `backend/app/api/routes/compliance.py`
- `frontend/app/dashboard/compliance/page.tsx`

---

### Phase 6 — Reviewer AI Engine

**Status:** Complete (backend, deterministic) / Partial (frontend)

**Implemented:**
- 6-dimension analysis (writing quality, research clarity, methodology, literature coverage, citation completeness, research gaps)
- Publication readiness score with label
- 2 API endpoints (analyze, get report)
- Deterministic analysis (no LLM/Ollama used)
- Frontend reviewer page (metrics + document list)

**Evidence:**
- `backend/app/services/reviewer/` (analyzer.py, schema.py)
- `backend/app/api/routes/reviewer.py`
- `frontend/app/dashboard/reviewer/page.tsx`

**Note:** Ollama, Qwen, Llama 3 are listed in ARCHITECTURE.md but never used. The reviewer is entirely deterministic (rule-based scoring). LLM integration is not implemented.

---

### Phase 7 — Formatting Engine

**Status:** Complete (backend) / Partial (frontend)

**Implemented:**
- 7 templates (IEEE, ACM, Springer, Elsevier, APA, MLA, Nature)
- Template definitions with fonts, margins, headings, citation styles
- DOCX generation for IEEE format
- Format validation (struct check)
- 5 API endpoints (list templates, get template, preview, format, get formatting)
- Frontend formatting page (template selector + document list)

**Evidence:**
- `backend/app/services/formatting/` (engine.py, templates.py, schema.py)
- `backend/app/services/ieee_formatter.py`
- `backend/app/api/routes/formatting.py`
- `frontend/app/dashboard/formatting/page.tsx`

**Note:** Only IEEE DOCX generation is implemented. APA, MLA, ACM, Springer, Elsevier, Nature templates are defined but have no actual document generators. PDF generation not implemented.

---

### Phase 8 — Batch Processing Engine

**Status:** Complete (backend, in-memory) / Partial (frontend)

**Implemented:**
- Batch manager with job lifecycle (create, add files, start, cancel, delete)
- 7 API endpoints (create, add files, start, status, cancel, list, delete)
- Frontend batch page (job list with progress bars)

**Evidence:**
- `backend/app/services/batch/` (manager.py, schema.py)
- `backend/app/api/routes/batch.py`
- `frontend/app/dashboard/batch/page.tsx`

**Critical Issue:** Batch data stored in-memory — lost on server restart. No worker processes batch jobs; `start` only changes status.

---

### Phase 9 — Submission Package Generator

**Status:** Complete (backend, in-memory) / Partial (frontend)

**Implemented:**
- Component definitions (9 package components)
- Package builder with document generators
- 3 API endpoints (build, get, list)
- Frontend submission page (component cards + document list)

**Evidence:**
- `backend/app/services/submission/` (builder.py, schema.py)
- `backend/app/api/routes/submission.py`
- `frontend/app/dashboard/submission/page.tsx`

**Critical Issue:** Package store is in-memory — lost on restart. ZIP bundling not implemented. LaTeX generation is placeholder.

---

## Backend Audit

### API Routes (53 endpoints total)

| Category | Endpoints | Status |
|----------|-----------|--------|
| Root | `GET /` | **Working** |
| Health | `GET /api/v1/health/`, `GET /api/v1/health/ready` | **Working** |
| Auth | `POST /api/v1/auth/login`, `GET /api/v1/auth/me` | **Working** |
| Documents | 12 endpoints (upload, parse, analyze, structure, validate, plagiarism, get, list, delete, jobs, format) | **Working** |
| Citations | 3 endpoints (analyze, get report, health) | **Working** |
| Compliance | 4 endpoints (list journals, get journal, analyze, get report) | **Working** |
| Reviewer | 2 endpoints (analyze, get report) | **Working** |
| Formatting | 5 endpoints (list templates, get template, preview, format, get) | **Working** |
| Export | 3 endpoints (request, list, download) | **Working** |
| Batch | 7 endpoints (create, add files, start, status, cancel, list, delete) | **Partial** |
| Submission | 3 endpoints (build, get, list) | **Partial** |

### Services

| Service | Status | Notes |
|---------|--------|-------|
| `auth.py` | **Working** | Firebase JWT verification with X.509 cert extraction; mock token fallback |
| `document_service.py` | **Working** | REST-based Supabase CRUD with `ensure_user_exists` |
| `document_parser.py` | **Working** | Format dispatch with local file save |
| `storage_service.py` | **Partial** | Returns `None` when Supabase not configured; graceful degradation |
| `struct_service.py` | **Working** | Deterministic classification + backward compat |
| `citation/` | **Working** | Extraction, validation, DOI resolution |
| `compliance/` | **Working** | Rule-based compliance checks |
| `reviewer/` | **Working** | Deterministic scoring only |
| `formatting/` | **Partial** | Only IEEE DOCX generation works |
| `batch/` | **Partial** | In-memory store; no actual processing |
| `submission/` | **Partial** | In-memory store; no ZIP/LaTeX generation |
| `ieee_formatter.py` | **Working** | IEEE DOCX generation |
| `plagiarism_service.py` | **Untested** | Existing but E2E tests don't verify |
| `pdf_service.py` | **Untested** | Minimal implementation |
| `ai_service.py` | **Untested** | Minimal implementation |

### Workers

| Worker | Status | Notes |
|--------|--------|-------|
| `parse_worker.py` | **Working** | Fetches pending jobs, downloads file, runs parse, enqueues classify |
| `structure_worker.py` | **Working** | Runs structure analysis on parsed doc |
| `citation_worker.py` | **Working** | Runs citation analysis on structured doc |
| `format_worker.py` | **Working** | Runs formatting on structured doc |
| `classify_worker.py` | **Untested** | Exists but classification pipeline not fully wired |
| `plagiarism_worker.py` | **Untested** | Exists but not tested |

**Critical Issue:** No worker supervisor/running — workers must be invoked manually.

### Authentication

| Component | Status | Notes |
|-----------|--------|-------|
| Firebase JWT Verification | **Working** | X.509 cert → public key extraction fixed |
| Mock Token Fallback | **Working** | `mock-user-123` when Firebase not configured |
| Auth Middleware | **Working** | `get_current_user` on all protected routes |
| Google Sign-In | **Working** | Frontend `signInWithPopup` implemented |

### Storage

| Component | Status | Notes |
|-----------|--------|-------|
| Supabase Storage Upload | **Partial** | Uses `manuscripts` bucket; returns `None` if unconfigured |
| File Download | **Partial** | `download_file_from_supabase` implemented but E2E not tested |
| Public URL Generation | **Partial** | Basic URL construction |

---

## Frontend Audit

### Pages

| Page | Route | Status | Notes |
|------|-------|--------|-------|
| Landing | `/` | **Working** | Full landing page with hero, features, CTA |
| Login | `/login` | **Working** | Google sign-in button |
| Dashboard (Workspace) | `/dashboard` | **Working** | Upload dropzone + journal selector + recent docs |
| Documents | `/dashboard/documents` | **Working** | Document list with status badges |
| Document Detail | `/dashboard/document/[id]` | **Working** | Document info, metrics, structure, jobs |
| Citations | `/dashboard/citations` | **Partial** | Reads `structured_json` directly instead of calling citation API |
| Compliance | `/dashboard/compliance` | **Partial** | Backend journal data not fetched; hardcoded list |
| Reviewer | `/dashboard/reviewer` | **Partial** | Reads `review_report` from doc object |
| Formatting | `/dashboard/formatting` | **Partial** | Template list hardcoded instead of API call |
| Batch | `/dashboard/batch` | **Partial** | Lists jobs but can't create/start from UI |
| Submission | `/dashboard/submission` | **Partial** | Lists docs but can't build packages from UI |
| Reports | `/dashboard/reports` | **Partial** | Plagiarism reports with document selector |
| Settings | `/dashboard/settings` | **Missing** | 404 — route referenced in nav but no file exists |

### Missing APIs (Frontend not consuming)

- `/api/v1/documents/{id}/citations/analyze` — not called from UI
- `/api/v1/documents/{id}/citations/health` — not called from UI
- `/api/v1/documents/{id}/compliance/analyze` — not called from UI
- `/api/v1/documents/{id}/review/analyze` — not called from UI
- `/api/v1/documents/{id}/formatting/format` — not called from UI
- `/api/v1/documents/{id}/formatting/preview` — not called from UI
- `/api/v1/documents/{id}/submission/build` — not called from UI
- `/api/v1/documents/{id}/submission` — not called from UI
- `/api/v1/batch/create` — not called from UI
- `/api/v1/compliance/journals` — not called (hardcoded list)
- `/api/v1/formatting/templates` — not called (hardcoded list)

### Missing UI

- **Citation Center** — No interactive citation-to-reference linking
- **Compliance analysis UI** — No "Run Analysis" button per document
- **Reviewer analysis UI** — No "Run Review" button per document
- **Formatting UI** — No "Format Document" button per document
- **Batch creation UI** — No file upload + batch create flow
- **Submission build UI** — No "Build Package" button
- **Export download** — Not wired in frontend
- **Settings page** — Entirely missing

### Placeholder Components

- Citations page: Shows metrics from `structured_json` but doesn't call citation API
- Compliance page: Journal list hardcoded; doesn't fetch from backend
- Formatting page: Template list hardcoded; no format action
- Batch page: Shows jobs but can't create them
- Submission page: Shows components but can't build

### Mock Data Usage

- Backend: `mock-user-123` used when Firebase not configured
- Backend: Fallback UUID when Supabase insert fails
- Frontend: `process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"` in every page

---

## Database Audit

### Tables (Defined in `database/full_schema.sql`)

| Table | Status | Notes |
|-------|--------|-------|
| `users` | **Created** | Idempotent, FK target for documents |
| `documents` | **Created** | Core table with JSONB columns for reports |
| `jobs` | **Created** | Processing job queue |
| `exports` | **Created** | Export records |
| `plagiarism_checks` | **Created** | Plagiarism reports |
| `citations` | **Created** | Citation records |
| `references_table` | **Created** | Reference records |
| `compliance_reports` | **Created** | Compliance check results |
| `review_reports` | **Created** | Review analysis results |
| `templates` | **Created** | Formatting templates (7 default rows) |
| `batch_jobs` | **Created** | Batch processing jobs |
| `submission_packages` | **Created** | Submission package records |

### Relationships

- `documents.user_id` → `users.id` (FK, CASCADE DELETE)
- `jobs.document_id` → `documents.id` (FK, CASCADE DELETE)
- `exports.document_id` → `documents.id` (FK, CASCADE DELETE)
- `plagiarism_checks.document_id` → `documents.id` (FK, CASCADE DELETE)
- `citations.document_id` → `documents.id` (FK, CASCADE DELETE)
- `references_table.document_id` → `documents.id` (FK, CASCADE DELETE)
- `compliance_reports.document_id` → `documents.id` (FK, CASCADE DELETE)
- `review_reports.document_id` → `documents.id` (FK, CASCADE DELETE)
- `submission_packages.document_id` → `documents.id` (FK, CASCADE DELETE)
- `batch_jobs.user_id` → `users.id` (FK, CASCADE DELETE)

### Indexes

All 12+ indexes defined in schema (user_id, status, created_at, document_id FK indexes)

### RLS Policies

All 12 tables have RLS enabled with per-user policies

### Issues

- Schema SQL exists but NOT verified as executed against Supabase
- Code stores reports inline in `documents.parsed_json` instead of using dedicated tables
- `documents.file_type` — code infers from filename; column exists but may not be populated
- `documents.selected_journal` — column exists but no backend PATCH endpoint

### Database Health Score: **75%**

---

## Integration Audit

### End-to-End Flow

```
Upload → Storage → Parsing → Database → Frontend Display
```

| Stage | Status | Details |
|-------|--------|---------|
| **Upload** | **Working** | File saved locally, parsed, record created in Supabase |
| **Storage (Supabase)** | **Partial** | Returns `None` when unconfigured; core flow works without it |
| **Parsing** | **Working** | DOCX, Markdown confirmed; PDF untested live |
| **Database Insert** | **Working** | `ensure_user_exists` fix applied; FK constraint satisfied |
| **Document Retrieval** | **Working** | GET by ID with ownership check |
| **Structure Analysis** | **Working** | Deterministic classification; endpoint returns results |
| **Citation Analysis** | **Working** | Backend endpoint works; not called from frontend |
| **Compliance Analysis** | **Working** | Backend endpoint works; not called from frontend |
| **Reviewer Analysis** | **Working** | Backend endpoint works; not called from frontend |
| **Formatting** | **Partial** | Only IEEE DOCX; other templates defined but not implemented |
| **Export** | **Partial** | Creates job but no auto-processing |
| **Batch Processing** | **Broken** | In-memory store; no actual worker processing |
| **Submission Package** | **Broken** | In-memory store; no ZIP/LaTeX generation |
| **Frontend Display** | **Partial** | Shows documents; analysis results not fetched via API |

---

## Error Resolution Log

### Resolved Issues

#### 1. Turbopack Root Route Crash
- **Root Cause:** Next.js Turbopack incompatibility with root route
- **Resolution:** Modified routing configuration
- **Current Status:** **Fixed** (commit `3ff0328`)

#### 2. Fast Refresh Infinite Loop
- **Root Cause:** React hot reload infinite re-render
- **Resolution:** Adjusted component boundaries
- **Current Status:** **Fixed** (commit `1c5de39`)

#### 3. Backend Startup Crash (5 Issues)
- **Root Cause:** 4 route files imported `DocumentService` as class (exports are module-level functions); 3 Pydantic validation errors for missing defaults; 1 wrong function name import
- **Resolution:** Changed to module imports; added Pydantic defaults; fixed function name
- **Current Status:** **Fixed** (commit `869f9fb`, `d8bbad5`)

#### 4. Firebase Token Verification
- **Root Cause:** PyJWT requires `-----BEGIN PUBLIC KEY-----` format; Google returns X.509 certificates
- **Resolution:** Extract `SubjectPublicKeyInfo` from X.509 cert using `cryptography` library
- **Current Status:** **Fixed** (commit `c9cd8a6`)

#### 5. SQL Schema PostgreSQL Compatibility
- **Root Cause:** `CREATE POLICY IF NOT EXISTS` not supported in older PostgreSQL versions
- **Resolution:** Changed to `DROP POLICY IF EXISTS` + `CREATE POLICY` pattern
- **Current Status:** **Fixed** (commit `d8bbad5`)

#### 6. Upload Document ID Becomes `"None"` String
- **Root Cause:** `str(None)` = `"None"` in Python when Supabase insert fails silently
- **Resolution:** Added fallback UUID generation + validation in route handler
- **Current Status:** **Fixed** (commit `5868567`)

#### 7. Foreign Key Constraint Violation on User
- **Root Cause:** `documents.user_id` references `users.id` but real Firebase users not inserted
- **Resolution:** Added `ensure_user_exists()` to create user row before document insert
- **Current Status:** **Fixed** (commit `d598761`)

#### 8. Auth Bypass in Delete/Export Endpoints
- **Root Cause:** Condition `if doc.get("user_id") and doc.get("user_id") != ...` short-circuits when `user_id` is None
- **Resolution:** Changed to direct comparison `if doc.get("user_id") != current_user.get("id")`
- **Current Status:** **Fixed** (System Audit)

#### 9. Null Filename Crash in Structure Analysis
- **Root Cause:** `os.path.splitext(None)` → TypeError
- **Resolution:** Added `doc.get("filename") or ""` guard
- **Current Status:** **Fixed** (System Audit)

#### 10. Worker Referenced `structured_json` Column
- **Root Cause:** Workers referenced non-existent `structured_json` column instead of `parsed_json`
- **Resolution:** Changed all references to `parsed_json`
- **Current Status:** **Fixed** (System Audit)

#### 11. Frontend Missing Environment Variable
- **Root Cause:** `NEXT_PUBLIC_API_BASE` not set; every fetch falls back to `http://localhost:8000`
- **Resolution:** Documented in reports; `.env.local.example` created
- **Current Status:** **Deferred** (needs Vercel env config)

#### 12. Backend Secrets in Frontend `.env`
- **Root Cause:** `DATABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` present in frontend `.env`
- **Resolution:** Cleaned; `.env.local.example` created with only frontend-safe vars
- **Current Status:** **Fixed** (SYSTEM_VALIDATION_REPORT)

#### 13. No dotenv Loader
- **Root Cause:** `.env` never loaded by Python application
- **Resolution:** Added `python-dotenv` + `load_dotenv()` in `main.py`
- **Current Status:** **Fixed** (SYSTEM_VALIDATION_REPORT)

#### 14. CORS Blocking Production
- **Root Cause:** `allow_origins=["http://localhost:3000"]` only
- **Resolution:** Added Vercel preview + production origins
- **Current Status:** **Fixed** (needs env var for dynamic origin)

---

## Known Issues

### Critical
| Issue | Details |
|-------|---------|
| **Batch/Submission in-memory stores** | All batch jobs and submission packages lost on server restart. Data NOT persisted to database despite schema tables existing. |
| **No worker supervisor** | Workers exist (`parse_worker.py`, etc.) but no scheduler/supervisor runs them. Jobs stay in "pending" state forever. |
| **Analysis endpoints not called from frontend** | Citation, compliance, reviewer, formatting APIs exist but frontend pages never invoke them. Users see empty reports. |
| **Settings page 404** | Navigation link exists but `/dashboard/settings` page file is missing. |

### High
| Issue | Details |
|-------|---------|
| **PPTX not supported** | `doc` file type reference in ARCHITECTURE.md but DOC is not in `ALLOWED_EXTENSIONS` |
| **Only IEEE formatting works** | 7 templates defined but only IEEE has a DOCX generator |
| **PDF parsing not live-tested** | PyMuPDF installed but E2E tests only use DOCX/Markdown |
| **`NEXT_PUBLIC_API_BASE` defaults to localhost** | Every page hardcodes fallback; production deployment will fail without env config |
| **No PATCH endpoint for documents** | Frontend tries to PATCH `selected_journal` but no endpoint exists |
| **Export jobs not auto-processed** | Export creates a "pending" job but no worker processes it |
| **NLP dependencies not installed** | spaCy, transformers, sentence-transformers, torch all commented out |
| **LLM reviewer not implemented** | Reviewer is entirely deterministic; Ollama/Qwen/Llama never used |

### Medium
| Issue | Details |
|-------|---------|
| **`window.location.href` used instead of `router.push`** | 5 pages use `window.location.href` for navigation |
| **Hardcoded localhost fallback in 9 pages** | `process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"` repeated |
| **Unused imports in 5+ files** | Frontend page imports not all used |
| **`apiFetch` doesn't handle non-JSON responses** | No `response.text()` fallback for 204/empty responses |
| **Plagiarism service untested** | `plagiarism_service.py` exists but not verified in E2E |
| **`classify_worker.py` not integrated** | Worker exists but classification pipeline not fully wired |
| **No rate limiting** | API has no rate limiting on any endpoint |
| **No input validation** | Request body validation is minimal |
| **Print-based logging** | All services use `print()` instead of proper logging |

### Low
| Issue | Details |
|-------|---------|
| **Journal selection not persisted** | PATCH fails silently; journal chosen but not saved |
| **Storage not required for core flow** | `storage_service.upload_file_to_supabase()` returns `None` when unconfigured |
| **No test files** | Zero test files in repository (no `tests/` directory) |
| **CORS origins hardcoded** | Should be environment variable |
| **Batch/Submission not migrated to database** | In-memory acceptable for v1 but needs migration |
| **LaTeX generation placeholder** | Submission package LaTeX is placeholder only |

---

## Technical Debt

### Duplicate Code
- `process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000"` repeated in all 10 dashboard pages
- `useAuth()` + `fetchDocuments()` pattern repeated identically in 8 pages

### Unused Services
- `ai_service.py` — minimal implementation, not referenced
- `pdf_service.py` — minimal implementation, not referenced
- `plagiarism_service.py` — exists but E2E tests skip it
- `classify_worker.py` — not part of any active workflow

### Dead Routes
- `POST /api/v1/documents/structure/validate` — validation endpoint but not used by frontend
- `GET /api/v1/documents/download/{export_id}` — export download, not wired in frontend

### Placeholder Implementations
- All frontend analysis pages (citations, compliance, reviewer, formatting) are essentially read-only list views
- Batch processing: `start_job` only changes status; no actual processing
- Submission package: No ZIP generation, LaTeX placeholder
- Templates (ACM, Springer, Elsevier, APA, MLA, Nature): Defined but no document generators
- Landing page "View Demo" button scrolls to non-functional section

### Mock Data
- `mock-user-123` — hardcoded mock user when Firebase not configured
- Fallback UUID — document record not actually in database when Supabase fails

---

## Release Readiness

| Area | Ready % | Notes |
|------|---------|-------|
| **Upload Pipeline** | 90% | File save, parse, DB insert working; storage optional |
| **Parsing** | 85% | DOCX/MD working; PDF untested live; LaTeX untested |
| **Structure Intelligence** | 80% | Deterministic classifier works; no NLP model integration |
| **Citation Intelligence** | 75% | Backend complete but no frontend integration |
| **Compliance Engine** | 75% | Backend complete but no frontend integration |
| **Reviewer Engine** | 70% | Deterministic only; no LLM; no frontend integration |
| **Formatting Engine** | 40% | Only IEEE DOCX; 6/7 templates unimplemented |
| **Export Engine** | 30% | Creates jobs but no auto-processing; PDF missing |
| **Batch Processing** | 25% | In-memory; no actual processing; no create UI |
| **Submission Package** | 25% | In-memory; no ZIP; no LaTeX; no build UI |
| **UI/UX** | 60% | Good landing page + layout; analysis UIs all placeholder |
| **Deployment** | 40% | Frontend/backend code ready; env configs incomplete; database schema not applied |

---

## Recommended Next Phase

### Immediate Priority
1. **Apply database schema** — Run `database/full_schema.sql` in Supabase SQL Editor (all 12 tables, indexes, RLS, default templates)
2. **Fix Settings page** — Create `/dashboard/settings` page (currently 404)
3. **Configure Vercel env** — Set `NEXT_PUBLIC_API_BASE` to Render backend URL

### Required Fixes Before V1
4. **Wire analysis endpoints to frontend** — Each analysis page should call its respective API (citation, compliance, reviewer, formatting)
5. **Migrate batch/submission to database** — Replace in-memory stores with Supabase tables
6. **Deploy worker supervisor** — Add scheduler/cron to run `parse_worker.py` and other workers
7. **Auto-process exports** — Worker should pick up "pending" format jobs

### Safe Next Phase
**Phase 10: Integration & Deployment**
- Wire all frontend pages to backend APIs
- Deploy backend to Render
- Deploy frontend to Vercel
- Configure environment variables
- Run database migrations
- End-to-end testing with real Firebase auth
- Add worker scheduler
