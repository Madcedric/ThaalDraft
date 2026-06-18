# ThaalDraft Fix Plan

**Date:** 2026-06-18
**Status:** Phase 1 Complete, Phase 2-4 Ready for Implementation

---

## Phase 1: Critical Fixes (COMPLETED)

| Fix | File | Change | Status |
|---|---|---|---|
| Fix DocumentService import | `compliance.py` | Changed class import to module import | DONE |
| Fix DocumentService import | `reviewer.py` | Changed class import to module import | DONE |
| Fix DocumentService import | `formatting.py` | Changed class import to module import | DONE |
| Fix DocumentService import | `submission.py` | Changed class import to module import | DONE |
| Fix Pydantic default | `structure/schema.py` | Added `default=0.0` for `overall_confidence` | DONE |
| Fix Pydantic Optional | `structure/schema.py` | Changed `processing_metadata` to `Optional` | DONE |
| Fix citation import | `citation/__init__.py` | Changed `extract_citations` to `extract_citations_from_text` | DONE |
| Fix Pydantic default | `reviewer/schema.py` | Added `default=0.0` for `overall` | DONE |
| Fix dict access | `compliance.py` | Changed `doc.user_id` to `doc.get("user_id")` | DONE |
| Fix dict access | `reviewer.py` | Changed `doc.user_id` to `doc.get("user_id")` | DONE |
| Fix dict access | `formatting.py` | Changed `doc.user_id` to `doc.get("user_id")` | DONE |
| Fix dict access | `submission.py` | Changed `doc.user_id` to `doc.get("user_id")` | DONE |

**Verification:** Backend starts successfully, all 53 endpoints respond.

---

## Phase 2: Schema Fixes (TODO)

| Fix | File | Change | Priority |
|---|---|---|---|
| Create full schema SQL | `database/full_schema.sql` | All 12 tables with indexes and RLS | HIGH |
| Add missing tables | Supabase | `citations`, `references_table`, `compliance_reports`, `review_reports`, `templates`, `batch_jobs`, `submission_packages` | HIGH |
| Add missing columns | `documents` table | `citation_report`, `compliance_report`, `review_report`, `selected_journal` | HIGH |

**Action:** Run `database/full_schema.sql` in Supabase SQL Editor.

---

## Phase 3: API Fixes (TODO)

| Fix | File | Change | Priority |
|---|---|---|---|
| Add dotenv loader | `backend/app/main.py` | Load `.env` file on startup | HIGH |
| Update CORS | `backend/app/main.py` | Add production frontend origin | HIGH |
| Create frontend env | `frontend/.env.local` | Set `NEXT_PUBLIC_API_BASE` | HIGH |
| Clean frontend env | `frontend/.env` | Remove `DATABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY` | MEDIUM |

---

## Phase 4: Frontend Fixes (TODO)

| Fix | File | Change | Priority |
|---|---|---|---|
| Add API rewrites | `frontend/next.config.ts` | Proxy `/api/*` to backend for local dev | HIGH |
| Centralize fetch calls | All dashboard pages | Use `services/api.ts` `apiFetch`/`authFetch` | MEDIUM |
| Add error handling | All dashboard pages | Global "Failed to fetch" handler | MEDIUM |

---

## Deployment Checklist

### Backend (Render)
- [ ] Set environment variables: `SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `FIREBASE_PROJECT_ID`
- [ ] Run `database/full_schema.sql` in Supabase SQL Editor
- [ ] Deploy backend to Render
- [ ] Update CORS with Render backend URL
- [ ] Verify `/api/v1/health/` returns 200

### Frontend (Vercel)
- [ ] Set `NEXT_PUBLIC_API_BASE` to Render backend URL
- [ ] Deploy frontend to Vercel
- [ ] Verify landing page loads
- [ ] Verify login works
- [ ] Verify dashboard loads without "Failed to fetch"

### Supabase
- [ ] Run `database/full_schema.sql`
- [ ] Verify all 12 tables created
- [ ] Verify RLS policies active
- [ ] Verify storage bucket `thaaldraft` exists
