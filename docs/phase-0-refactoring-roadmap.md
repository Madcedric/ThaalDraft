# Phase 0 — Refactoring Roadmap

**Generated:** June 16, 2026
**Based on:** UI Audit, Architecture Audit, Database Audit

---

## Recommended Changes

### Priority 1 — Architecture Refactor (Phase 1)

**Goal:** Establish clean folder structure and separation of concerns.

| Task | Scope | Risk | Effort |
|---|---|---|---|
| Create `frontend/services/` layer | Extract all `fetch()` calls from page components into typed API service functions | LOW | MEDIUM |
| Create `frontend/hooks/` directory | Extract auth, upload, and document logic into reusable custom hooks | LOW | LOW |
| Create `frontend/types/` directory | Define shared TypeScript interfaces (Document, Job, User, etc.) | LOW | LOW |
| Create `frontend/utils/` directory | Move utility functions (API_BASE, formatDate, etc.) from inline | LOW | LOW |
| Refactor `lib/auth-context.tsx` | Split into `AuthProvider`, `useAuth`, `useAuthGuard` hooks | MEDIUM | LOW |
| Move `shadcn` to devDependencies | Fix package.json dependency classification | LOW | LOW |

### Priority 2 — Backend Foundation (Phase 2)

**Goal:** Fix critical backend issues and establish proper service architecture.

| Task | Scope | Risk | Effort |
|---|---|---|---|
| Replace OpenAI with Ollama/Qwen | Rewrite `ai_service.py` to use local LLM | MEDIUM | HIGH |
| Uncomment AI dependencies | Enable spacy, sentence-transformers, chromadb in requirements.txt | MEDIUM | LOW |
| Fix `user_id` injection | Add `current_user["id"]` to document creation payloads | LOW | LOW |
| Add rule-based section classifier | Deterministic fallback before LLM classification | LOW | MEDIUM |
| Fix worker job_type filter | Pass `job_type="parse"` to `fetch_pending_job()` | LOW | LOW |
| Fix `datetime.utcnow()` | Replace with `datetime.now(timezone.utc)` in all workers | LOW | LOW |
| Add `DEVELOPMENT_MODE` guard | Block mock tokens in production | LOW | LOW |

### Priority 3 — Database Schema (Phase 3)

**Goal:** Add missing entities and fix schema integrity issues.

| Task | Scope | Risk | Effort |
|---|---|---|---|
| Fix `user_id` NOT NULL | Add constraint to `documents` table | LOW | LOW |
| Fix RLS policy syntax | Wrap `CREATE POLICY IF NOT EXISTS` in `DO` blocks | LOW | LOW |
| Add `subscriptions` table | SaaS tier tracking | LOW | MEDIUM |
| Add `citations` and `references` tables | Citation intelligence module | MEDIUM | MEDIUM |
| Add `compliance_reports` table | Journal compliance module | MEDIUM | MEDIUM |
| Add `review_reports` table | Reviewer AI module | MEDIUM | MEDIUM |
| Add missing indexes | `jobs.document_id`, `plagiarism_checks.document_id`, `exports.document_id` | LOW | LOW |

### Priority 4 — Frontend Pages (Phase 4)

**Goal:** Complete missing pages and fix UI/UX issues.

| Task | Scope | Risk | Effort |
|---|---|---|---|
| Create `/dashboard/documents` page | Document list with search/filter | LOW | MEDIUM |
| Create `/dashboard/settings` page | User profile and preferences | LOW | LOW |
| Refactor document detail page | Use Shadcn components, fix `alert()`, add error boundary | LOW | MEDIUM |
| Refactor reports page | Use Shadcn components, add report visualization | LOW | MEDIUM |
| Add mobile menu to landing page | Hamburger drawer for mobile navigation | LOW | LOW |
| Fix login page tokens | Replace hardcoded `bg-[#0a0a0f]` with `bg-background` | LOW | LOW |
| Add skip-to-content link | Accessibility improvement | LOW | LOW |

### Priority 5 — Backend Services (Phase 5)

**Goal:** Complete missing backend functionality.

| Task | Scope | Risk | Effort |
|---|---|---|---|
| Add document list endpoint | `GET /api/v1/documents` with pagination | LOW | LOW |
| Add document delete endpoint | `DELETE /api/v1/documents/{id}` | LOW | LOW |
| Fix CORS configuration | Move to environment variable | LOW | LOW |
| Fix readiness probe | Add real Supabase/Firebase connectivity checks | LOW | LOW |
| Fix export download route | Include `{document_id}` in path | LOW | LOW |
| Add Pydantic request models | Validate all endpoint inputs | LOW | MEDIUM |
| Fix author extraction | Populate `authors` field in `docx_parser.py` | MEDIUM | MEDIUM |

### Priority 6 — Formatting Engine (Phase 6)

**Goal:** Support all required journal formats.

| Task | Scope | Risk | Effort |
|---|---|---|---|
| Add APA template | APA 7th edition formatting | MEDIUM | HIGH |
| Add MLA template | MLA 9th edition formatting | MEDIUM | HIGH |
| Add ACM template | ACM proceedings formatting | MEDIUM | HIGH |
| Add Springer template | Springer LNCS formatting | MEDIUM | HIGH |
| Add Elsevier template | Elsevier journal formatting | MEDIUM | HIGH |
| Add IEEE two-column layout | Fix single-column to proper IEEE format | MEDIUM | MEDIUM |

### Priority 7 — Citation Intelligence (Phase 7)

**Goal:** Build citation analysis and recommendation engine.

| Task | Scope | Risk | Effort |
|---|---|---|---|
| Improve citation extraction | Support all common citation formats | MEDIUM | HIGH |
| Add citation validation | Cross-check citations against references list | MEDIUM | MEDIUM |
| Integrate OpenAlex | Reference discovery API | MEDIUM | MEDIUM |
| Integrate CrossRef | DOI validation API | MEDIUM | MEDIUM |
| Integrate Semantic Scholar | Citation recommendations API | MEDIUM | MEDIUM |

### Priority 8 — Compliance & Review (Phase 8)

**Goal:** Build journal compliance validation and reviewer AI.

| Task | Scope | Risk | Effort |
|---|---|---|---|
| Add compliance validation | Word count, abstract length, citation style checks | MEDIUM | HIGH |
| Add reviewer AI | Writing quality, methodology, literature coverage feedback | MEDIUM | HIGH |
| Replace plagiarism toy algorithm | Sentence Transformers + ChromaDB | MEDIUM | HIGH |

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|---|---|---|---|
| Ollama model quality below OpenAI | MEDIUM | HIGH | Rule-based classifier as primary tier; LLM as fallback |
| RLS policy rewrite breaks existing data | LOW | HIGH | Test migration on staging before production |
| Missing dependencies cause import errors | LOW | MEDIUM | Install and test one dependency at a time |
| Worker race condition causes duplicate processing | MEDIUM | MEDIUM | Add `SELECT FOR UPDATE SKIP LOCKED` pattern |
| Breaking changes in existing API consumers | LOW | HIGH | Maintain backward compatibility; version API |

---

## Priority Order Summary

| Phase | Focus | Key Deliverables |
|---|---|---|
| **Phase 1** | Architecture Refactor | services/, hooks/, types/, utils/ directories; clean folder structure |
| **Phase 2** | Backend Foundation | Ollama integration, rule-based classifier, user_id fix, worker fixes |
| **Phase 3** | Database Schema | Missing tables (citations, references, compliance, review), schema fixes |
| **Phase 4** | Frontend Pages | Document list, settings, mobile nav, accessibility fixes |
| **Phase 5** | Backend Services | Document CRUD, CORS, readiness, Pydantic models |
| **Phase 6** | Formatting Engine | APA, MLA, ACM, Springer, Elsevier templates |
| **Phase 7** | Citation Intelligence | Citation extraction, validation, OpenAlex/CrossRef/Semantic Scholar |
| **Phase 8** | Compliance & Review | Compliance validation, reviewer AI, plagiarism upgrade |

---

## Success Criteria

| Metric | Target | Current |
|---|---|---|
| Frontend folder structure | services/, hooks/, types/, utils/ | None |
| Backend services architecture | Isolated, modular services | Monolithic services/ |
| Missing critical tables | 0 | 5 (projects, citations, references, compliance_reports, review_reports) |
| AI policy compliance | 100% open-source | OpenAI API used |
| Journal format support | 6 formats | 1 (IEEE only) |
| Accessibility compliance | WCAG AA | Not tested |
| Build status | Clean | Clean (3 pre-existing lint warnings) |

---

**Phase 0 complete. Ready for Phase 1 execution.**
