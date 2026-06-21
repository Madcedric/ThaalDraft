# ThaalDraft V2 Implementation Roadmap

## Branch Strategy
All work must be done on the `v2-rearchitecture` branch. Do not modify the existing `main` or `develop` branch until V2 is fully approved.

## Phase 1: Foundation & Database Migration
1. Set up the `v2-rearchitecture` branch.
2. Apply the new `DATABASE_SCHEMA_V2.sql` to a fresh Supabase environment.
3. Refactor `backend/app/services/document_service.py` to use the new normalized schema instead of `JSONB`.
4. Fix the upload failure root cause by ensuring the Firebase `user_id` is properly synchronized in the `users` table prior to document insertion.

## Phase 2: Asynchronous Infrastructure
1. Integrate Redis and a task queue (e.g., Celery, RQ, or FastAPI BackgroundTasks).
2. Refactor existing synchronous parsing logic in `documents.py` into async workers.
3. Implement WebSocket endpoints for real-time progress updates to the frontend.

## Phase 3: AI & Citation Intelligence
1. Create `ai_providers/` module to abstract Gemini and DeepSeek.
2. Completely remove `ollama_service.py`.
3. Integrate Semantic Scholar alongside CrossRef and OpenAlex in the citation validation worker.

## Phase 4: Frontend Modernization
1. Build the new 3-pane Workspace UI (Structure, Live Manuscript, Analysis).
2. Implement WebSocket client connections to listen for job status changes.
3. Create the Mode Selector (Reconstruction vs Formatting Studio).

## Phase 5: Formatting Studio & Export
1. Integrate LaTeX generation for Elsevier, Springer, and Nature templates.
2. Build the Submission Package generator (ZIP bundler).

## Phase 6: Validation & Deployment
1. Run full end-to-end testing of the pipeline.
2. Deploy backend to Render and frontend to Vercel.
3. Generate final completion report.
