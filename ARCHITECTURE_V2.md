# ThaalDraft V2 Architecture

## Overview
ThaalDraft V2 transitions from a monolithic, synchronous processing model to an asynchronous, decoupled, and event-driven architecture designed for high reliability and scalability. 

## Key Architectural Changes
1. **Asynchronous Background Processing**: All parsing, structural extraction, citation validation, and formatting will run as background jobs (e.g., using Redis and Celery/Arq). 
2. **Relational Data Model**: Shifting from storing massive `JSONB` blobs (`parsed_json`) to a normalized schema (`manuscripts`, `sections`, `references`, `figures`).
3. **Event-Driven Frontend**: The React frontend will use WebSockets or Server-Sent Events (SSE) to receive real-time updates on job statuses instead of polling or waiting for synchronous responses.
4. **AI Strategy**: Removal of local Ollama inference in favor of Gemini (primary) and DeepSeek (fallback) for reasoning, structuring, and formatting.

## Component Architecture

### 1. Frontend (Next.js + React)
- **State Management**: Zustand or React Context for real-time job state.
- **Modes**: 
  - *Reconstruction Mode*: For raw drafts.
  - *Formatting Studio*: For structured manuscripts targeting specific journals.

### 2. Backend (FastAPI)
- **API Gateway**: Handles authentication (Firebase), rate limiting, and request routing.
- **Job Queue Producer**: Enqueues tasks for background workers.
- **WebSocket Server**: Broadcasts job completion/failure events to clients.

### 3. Workers (Python)
- **Extraction Worker**: Uses ZIP/XML for DOCX, PyMuPDF/OCR for PDFs.
- **AI Worker**: Interfaces with Gemini/DeepSeek for review and compliance.
- **Citation Worker**: Interfaces with CrossRef/OpenAlex/Semantic Scholar.
- **Formatting Worker**: Generates target outputs (LaTeX, DOCX, PDFs).

### 4. Persistence
- **Database**: Supabase PostgreSQL (Normalized schema).
- **Storage**: Supabase Storage (Raw uploads + Generated packages).
- **Queue**: Redis (Task queuing and state management).
