# ThaalDraft V2 — Project Audit Report

## 1. Project Overview & Architecture
ThaalDraft V1 is a monolithic application with a React (Next.js) frontend and a Python (FastAPI) backend.
The current architecture uses Firebase for authentication and Supabase (PostgreSQL + Storage) for persistence.

### Dependency Map
- **Frontend**: Next.js, React, Tailwind CSS, Shadcn UI
- **Backend**: FastAPI, PyMuPDF, python-docx, spaCy, sentence-transformers
- **Database**: Supabase PostgreSQL
- **Storage**: Supabase Storage
- **Auth**: Firebase Auth

### Module Status
- **Dead Code**: Several isolated Python scripts in `workers/` that act as one-shots rather than queue consumers.
- **Partially Implemented**: Formatting templates (IEEE, ACM, etc.) are hardcoded and not extensible.
- **Fake/Placeholder**: Custom journal builder and submission packages are UI mockups without backend persistence.
- **Synchronous Bottlenecks**: `documents.py` executes heavy PDF/DOCX parsing synchronously during the upload request, blocking the thread and leading to potential timeouts.

## 2. Broken Upload-Processing Chain
The upload process relies on a direct REST call to Supabase. If the insert fails (due to a foreign key constraint missing the Firebase user ID in the users table, or an RLS issue), the backend catches the exception but still returns a dynamically generated fallback UUID. The frontend assumes success but subsequent requests using this fake UUID fail with a 404 (Document not found).

## 3. Recommended Actions
- Completely restructure the database schema to normalize the `parsed_json` into relational tables (manuscripts, sections, figures).
- Implement an asynchronous job queue using Redis + Celery (or equivalent) to handle parsing and analysis.
- Replace any hardcoded or deterministic fake responses with robust, state-driven backend logic.
