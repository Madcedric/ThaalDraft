# ThaalDraft V2 — Architecture Audit Report

**Date:** 2025-06-21
**Branch:** thaaldraft-v2
**Baseline commit:** 5fd176a
**Scope:** Full V1 codebase vs V2 reference documents

---

## Executive Summary

The V1 codebase has **significant architectural debt** that must be addressed before V2 implementation. Key findings:

- **15 modules** must be removed (Ollama, duplicate services, dead code)
- **8 modules** must be completely rewritten
- **6 modules** can be reused with modifications
- **12 new modules** must be created
- **Database schema** requires complete restructuring (5 tables → 16 tables)
- **AI strategy** must change from Ollama to Gemini/DeepSeek abstraction
- **Frontend** requires major state-driven UI overhaul

---

## 1. V2 Architecture Compliance Audit

### 1.1 AI Strategy — CRITICAL GAP

| Requirement | V1 Status | Action |
|-------------|-----------|--------|
| Gemini API (Priority 1) | ❌ Not implemented | **CREATE** GeminiProvider |
| DeepSeek API (Priority 2) | ❌ Not implemented | **CREATE** DeepSeekProvider |
| AI Provider Abstraction | ❌ Not implemented | **CREATE** AIProviderAdapter |
| Ollama removal | ⚠️ Currently used | **REMOVE** ollama_service.py |
| Fallback: Gemini → DeepSeek → Error | ❌ Not implemented | **CREATE** fallback chain |

**Decision:** Ollama must be completely removed. Replace with Gemini-first, DeepSeek-second architecture.

### 1.2 Canonical Manuscript Model — PARTIAL

| Requirement | V1 Status | Action |
|-------------|-----------|--------|
| StructuredManuscript model | ✅ Exists (manuscript/model.py) | **ENRICH** with affiliations, citation_map, DOI_map |
| Single source of truth | ⚠️ Partial (stored in parsed_json JSONB) | **REFACTOR** to normalized tables |
| All modules read same model | ⚠️ Some use raw parsed_json | **ENFORCE** canonical model access |

### 1.3 Database Schema — MAJOR GAP

| V2 Table | V1 Equivalent | Action |
|----------|---------------|--------|
| `users` | ✅ Exists | **MODIFY** (add firebase_uid, photo_url) |
| `documents` | ✅ Exists | **MODIFY** (add mode, target_journal, selected_template) |
| `document_versions` | ❌ Missing | **CREATE** |
| `manuscripts` | ❌ In parsed_json JSONB | **CREATE** normalized table |
| `sections` | ❌ In parsed_json JSONB | **CREATE** normalized table |
| `figures` | ❌ In parsed_json JSONB | **CREATE** normalized table |
| `tables` | ❌ In parsed_json JSONB | **CREATE** normalized table |
| `references_table` | ❌ In parsed_json JSONB | **CREATE** normalized table |
| `doi_records` | ❌ Missing | **CREATE** |
| `citation_reports` | ❌ In parsed_json JSONB | **CREATE** |
| `compliance_reports` | ❌ In parsed_json JSONB | **CREATE** |
| `review_reports` | ❌ In parsed_json JSONB | **CREATE** |
| `formatting_jobs` | ⚠️ In-memory only | **CREATE** with persistence |
| `exports` | ✅ Exists (partial) | **MODIFY** |
| `submission_packages` | ⚠️ In-memory only | **CREATE** with persistence |
| `batch_jobs` | ⚠️ In-memory only | **CREATE** with persistence |
| `activity_logs` | ❌ Missing | **CREATE** |
| `journal_templates` | ❌ In code only | **CREATE** table + seed data |

### 1.4 Input Modes — PARTIAL

| Mode | V1 Status | Action |
|------|-----------|--------|
| Reconstruction Mode (DOCX, PDF, TXT, MD) | ⚠️ Partial (.tex supported, .txt not) | **ADD** .txt support |
| Formatting Studio Mode (DOCX, PDF, LaTeX) | ⚠️ Partial | **ENHANCE** with mode selection |

### 1.5 DOI Intelligence — PARTIAL

| Integration | V1 Status | Action |
|-------------|-----------|--------|
| CrossRef | ✅ Exists (citation/resolver.py) | **KEEP** |
| OpenAlex | ✅ Exists (citation/resolver.py) | **KEEP** |
| Semantic Scholar | ❌ Missing | **CREATE** |
| DOI extraction | ✅ Exists | **KEEP** |
| DOI validation | ✅ Exists | **KEEP** |
| Metadata enrichment | ⚠️ Partial | **ENHANCE** |

### 1.6 Formatting Studio — PARTIAL

| Template | V1 Status | Action |
|----------|-----------|--------|
| IEEE | ✅ Exists | **KEEP** |
| ACM | ✅ Exists | **KEEP** |
| Springer | ✅ Exists | **KEEP** |
| APA | ✅ Exists | **KEEP** |
| MLA | ✅ Exists | **KEEP** |
| Nature | ✅ Exists | **KEEP** |
| Elsevier | ⚠️ In templates.py only | **IMPLEMENT** |
| Custom Journal Builder | ❌ Missing | **CREATE** |

### 1.7 UI/UX — MAJOR GAP

| Requirement | V1 Status | Action |
|-------------|-----------|--------|
| State-driven UI | ❌ Static pages | **REBUILD** |
| Real-time updates | ❌ Manual refresh | **CREATE** WebSocket/SSE |
| Two upload modes | ❌ Single upload | **SPLIT** reconstruction vs formatting |
| Progress tracking | ⚠️ Basic status | **ENHANCE** |
| Error recovery | ❌ Missing | **CREATE** |
| Empty states | ⚠️ Basic | **ENHANCE** |
| No dead buttons | ⚠️ Some exist | **FIX** |

### 1.8 Workers & Job Queue — MAJOR GAP

| Requirement | V1 Status | Action |
|-------------|-----------|--------|
| Background job system | ⚠️ One-shot scripts | **REBUILD** proper job queue |
| Job status tracking | ⚠️ Basic (jobs table) | **ENHANCE** |
| Progress tracking | ❌ Missing | **CREATE** |
| Retry handling | ❌ Missing | **CREATE** |
| Failure reporting | ⚠️ Basic | **ENHANCE** |

---

## 2. Module-by-Module Audit

### 2.1 REMOVE — Modules to Delete

| Module | Reason | Impact |
|--------|--------|--------|
| `ollama_service.py` | V2 says "No Ollama in core architecture" | Reviewer AI must use Gemini/DeepSeek |
| `reviewer/analyzer.py` | Legacy v1, replaced by engine_v2.py | No impact |
| `formatting/engine.py` | Legacy v1, replaced by engine_v2.py | No impact |
| `struct_service.py` | Duplicate of manuscript/engine.py | Consolidate into manuscript/engine |
| `ai_service.py` | Thin wrapper around structure/classifier | Merge into structure engine |
| `format_service.py` | Duplicate of formatting/engine | Remove |
| `ieee_formatter.py` | Duplicate of formatting/engine_v2 | Remove |
| `workers/plagiarism_local_test.py` | Test file, not production | Remove |
| `workers/parse_worker.py` | One-shot script, not production job queue | Replace with proper worker |
| `workers/classify_worker.py` | One-shot script | Replace with proper worker |
| `workers/structure_worker.py` | One-shot script | Replace with proper worker |
| `workers/format_worker.py` | One-shot script | Replace with proper worker |
| `workers/citation_worker.py` | One-shot script | Replace with proper worker |
| `workers/plagiarism_worker.py` | One-shot script | Replace with proper worker |

### 2.2 REFACTOR — Modules to Rewrite

| Module | Current State | V2 Target |
|--------|--------------|-----------|
| `manuscript/model.py` | Basic StructuredManuscript | Add affiliations, citation_map, DOI_map |
| `manuscript/engine.py` | Rule-based classification | Add Gemini/DeepSeek for reconstruction |
| `formatting/engine_v2.py` | 6 templates | Add Elsevier, Custom Builder |
| `citation/analyzer.py` | Basic analysis | Add Semantic Scholar, DOI enrichment |
| `compliance/analyzer.py` | Basic rules | Add more journal rules |
| `document_service.py` | Direct Supabase REST | Add normalized table access |
| `storage_service.py` | Basic upload/download | Add versioning support |
| `export_engine.py` | DOCX/PDF only | Add LaTeX, ZIP package |
| `submission/builder.py` | Basic package | Add all 7 components |
| `batch/manager.py` | In-memory only | Persist to Supabase |

### 2.3 KEEP — Modules to Preserve

| Module | Reason |
|--------|--------|
| `auth.py` (service) | Firebase auth works well |
| `docx_parser.py` | Solid DOCX extraction |
| `pdf_parser.py` | Solid PDF extraction |
| `latex_parser.py` | Solid LaTeX extraction |
| `markdown_parser.py` | Solid Markdown extraction |
| `ocr_service.py` | OCR fallback works |
| `storage_service.py` | Supabase storage works |
| `user_service.py` | User CRUD works |
| `export_service.py` | Export persistence works |
| `citation/resolver.py` | CrossRef/OpenAlex work |
| `citation/extractor.py` | Citation extraction works |
| `citation/validator.py` | Citation validation works |
| `citation/rules.py` | Style detection works |
| `compliance/rules.py` | Journal rules work |
| `structure/classifier.py` | Section classification works |
| `structure/rules.py` | Rules work |

### 2.4 CREATE — New Modules

| Module | Purpose |
|--------|---------|
| `ai_providers/__init__.py` | AI provider abstraction |
| `ai_providers/base.py` | Abstract AI provider |
| `ai_providers/gemini.py` | Gemini API integration |
| `ai_providers/deepseek.py` | DeepSeek API integration |
| `ai_providers/fallback.py` | Fallback chain logic |
| `doi_intelligence/__init__.py` | DOI intelligence module |
| `doi_intelligence/semantic_scholar.py` | Semantic Scholar integration |
| `doi_intelligence/enrichment.py` | Reference enrichment |
| `custom_builder/__init__.py` | Custom journal builder |
| `custom_builder/schema.py` | Custom format schema |
| `custom_builder/engine.py` | Custom format engine |
| `realtime/__init__.py` | Real-time updates |
| `realtime/websocket.py` | WebSocket handler |
| `realtime/events.py` | Event definitions |
| `jobs/__init__.py` | Job queue system |
| `jobs/queue.py` | Job queue implementation |
| `jobs/worker.py` | Background worker |
| `jobs/retry.py` | Retry logic |
| `activity/__init__.py` | Activity logging |
| `activity/logger.py` | Activity log service |

---

## 3. Frontend Audit

### 3.1 Pages to Rebuild

| Page | V1 State | V2 Action |
|------|----------|-----------|
| `/dashboard` (Workspace) | Basic upload + recent | **REBUILD** hybrid view with mode selection |
| `/dashboard/documents` | Basic list | **REBUILD** with status-driven cards |
| `/dashboard/document/[id]` | Basic detail | **REBUILD** with live progress, all modules |
| `/dashboard/citations` | Overview only | **REBUILD** with DOI intelligence |
| `/dashboard/compliance` | Basic | **REBUILD** with journal picker |
| `/dashboard/reviewer` | Overview only | **REBUILD** with AI provider selection |
| `/dashboard/formatting` | Basic templates | **REBUILD** with custom builder |
| `/dashboard/batch` | Basic | **REBUILD** with proper queue |
| `/dashboard/submission` | Basic | **REBUILD** with all 7 components |
| `/dashboard/reports` | Placeholder | **REBUILD** with all report types |
| `/login` | Basic | **KEEP** with enhancements |

### 3.2 New Pages

| Page | Purpose |
|------|---------|
| `/dashboard/doi` | DOI Intelligence dashboard |
| `/dashboard/settings` | User settings, API keys, preferences |

### 3.3 Components to Create

| Component | Purpose |
|-----------|---------|
| `ModeSelector` | Reconstruction vs Formatting Studio |
| `ProgressBar` | Multi-step progress |
| `StatusBadge` | State-driven status |
| `LiveLog` | Real-time processing log |
| `ReportPanel` | Unified report display |
| `CustomFormatBuilder` | Custom journal format controls |
| `DOIResolver` | DOI resolution UI |
| `ActivityTimeline` | Activity history |

---

## 4. API Audit

### 4.1 Routes to Remove

| Route | Reason |
|-------|--------|
| `POST /documents/parse` | Merge into upload |
| `POST /documents/format` | Use formatting/format instead |

### 4.2 Routes to Add

| Route | Purpose |
|-------|---------|
| `GET /doi/{document_id}` | DOI intelligence report |
| `POST /doi/{document_id}/resolve` | Resolve all DOIs |
| `POST /doi/{document_id}/enrich` | Enrich references |
| `GET /formatting/custom` | Get custom format presets |
| `POST /formatting/custom` | Save custom format |
| `GET /activity/{document_id}` | Activity log |
| `WS /ws/{document_id}` | WebSocket for live updates |

### 4.3 Routes to Modify

| Route | Change |
|-------|--------|
| `POST /documents/upload` | Add mode parameter (reconstruction/formatting) |
| `POST /documents/{id}/review/analyze` | Switch from Ollama to Gemini/DeepSeek |
| `POST /documents/{id}/export` | Add LaTeX export option |
| `POST /documents/{id}/submission/build` | Add all 7 components |

---

## 5. Dependency Audit

### 5.1 Remove

| Dependency | Reason |
|------------|--------|
| `ollama` | No Ollama in V2 core |

### 5.2 Add

| Dependency | Purpose |
|------------|---------|
| `google-generativeai` | Gemini API |
| `httpx` | Async HTTP for DeepSeek |
| `websockets` | Real-time updates |
| `pdfplumber` | Enhanced PDF extraction |
| `redis` | Job queue (optional) |

### 5.3 Keep

| Dependency | Purpose |
|------------|---------|
| `fastapi` | Backend framework |
| `uvicorn` | ASGI server |
| `pydantic` | Data validation |
| `spacy` | NLP |
| `sentence-transformers` | Embeddings |
| `python-docx` | DOCX parsing |
| `PyMuPDF` | PDF parsing |
| `requests` | HTTP client |
| `firebase-admin` | Auth |

---

## 6. Migration Plan

### Phase 0: Reset and Audit ✅
- [x] Create V2 branch
- [x] Generate audit report
- [x] Define target architecture

### Phase 1: Document Intelligence Layer
- [ ] Enhance DOCX extractor (ZIP architecture)
- [ ] Enhance PDF extractor (pdfplumber + OCR)
- [ ] Add .txt support
- [ ] Create extraction report

### Phase 2: Canonical Manuscript JSON
- [ ] Enrich StructuredManuscript model
- [ ] Create normalized database tables
- [ ] Create persistence layer
- [ ] Create serializer/validator

### Phase 3: Structure Intelligence
- [ ] Create AI provider abstraction
- [ ] Implement Gemini provider
- [ ] Implement DeepSeek provider
- [ ] Enhance structure engine with AI
- [ ] Remove Ollama

### Phase 4: DOI and Citation Intelligence
- [ ] Add Semantic Scholar integration
- [ ] Create DOI enrichment workflow
- [ ] Enhance citation analysis

### Phase 5: Reviewer AI
- [ ] Implement Gemini review
- [ ] Implement DeepSeek fallback
- [ ] Remove deterministic fallback

### Phase 6: Formatting Studio
- [ ] Implement Elsevier template
- [ ] Create Custom Journal Builder
- [ ] Add LaTeX export option

### Phase 7: Export Engine
- [ ] Add LaTeX export
- [ ] Add ZIP package export
- [ ] Enhance export history

### Phase 8: Workspace and UI Modernization
- [ ] Rebuild workspace with hybrid view
- [ ] Add real-time updates (WebSocket)
- [ ] Add progress tracking
- [ ] Add error recovery
- [ ] Fix dead buttons

### Phase 9: Batch Processing and Submission
- [ ] Rebuild batch with Supabase persistence
- [ ] Implement all 7 submission components
- [ ] Add proper job queue

### Phase 10: Testing and Deployment
- [ ] End-to-end testing
- [ ] Performance testing
- [ ] Deployment checklist

---

## 7. Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Gemini API costs | High | Implement usage limits, caching |
| Database migration complexity | High | Phased migration, backward compatibility |
| Real-time updates complexity | Medium | Start with polling, upgrade to WebSocket |
| Custom builder complexity | Medium | Start with presets, add customization later |
| LaTeX compilation | Medium | Use external service, fallback to DOCX |

---

## 8. Success Criteria

- [ ] No Ollama in codebase
- [ ] All modules use canonical manuscript model
- [ ] Database normalized (not JSONB-heavy)
- [ ] Gemini/DeepSeek AI working
- [ ] DOI intelligence with Semantic Scholar
- [ ] Custom journal builder functional
- [ ] Real-time UI updates working
- [ ] No dead buttons or placeholder pages
- [ ] All 7 submission components working
- [ ] LaTeX export working
- [ ] Activity logging working
- [ ] Job queue with retry handling
- [ ] End-to-end flow complete: Upload → Reconstruct → Analyze → Review → Format → Export → Submit
