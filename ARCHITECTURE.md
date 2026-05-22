# ThaalDraft - Architecture Overview

This document summarizes the Phase 1 architecture and project layout for ThaalDraft.

## Tech Stack

- Frontend: Next.js (React)
- Backend: FastAPI (Python)
- Auth: Firebase Auth
- Database: Supabase (Postgres)
- Storage: Supabase Storage
- Document parsing: python-docx, Docling
- AI: OpenAI (NLP classification)

## High-level Services

- Frontend (Next.js): user UI, authentication flows, upload UI, dashboards.
- API (FastAPI): upload endpoints, parsing pipelines, formatting, classification, plagiarism checks.
- Storage: Supabase Storage for uploaded files and processed artifacts.
- Database: Supabase Postgres for structured document metadata and jobs.
- Auth: Firebase for user authentication; backend verifies tokens.

## Data Flow

1. User authenticates via Firebase in the frontend.
2. User uploads DOCX -> frontend sends to FastAPI upload endpoint.
3. FastAPI stores raw file in Supabase Storage (or local/uploads during dev).
4. Parsing (python-docx + Docling) extracts structure into JSON.
5. AI classification (OpenAI) labels sections and structure.
6. Formatting engines (IEEE/ACM) generate output DOCX/PDF stored in Storage.

## Development & Environment

- See `backend/.env.example` and `frontend/.env.example` for environment variables to configure.
- `backend/app/main.py` exposes health and document routes for local testing.

## Next Steps (Phase 2+)

- Phase 2: Implement authentication integration (Firebase tokens + user table in Supabase).
