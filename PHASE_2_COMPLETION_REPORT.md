# Phase 2 Completion Report

## Files Changed
- `backend/requirements.txt`: Added `websockets`.
- `backend/app/services/job_service.py`: Completely rewritten to interact with the new Supabase `batch_jobs` table. Added `claim_next_job` logic to securely poll and lock pending jobs.
- `backend/app/api/routes/documents.py`: Refactored the `POST /upload` endpoint. It now handles the initial upload, creates the document record, queues a `parse` job via `job_service`, and returns a quick 200 response rather than hanging synchronously.
- `backend/app/workers/queue_worker.py`: [NEW] A background worker that continuously polls Supabase `batch_jobs`, executes heavy document extraction, saves the structured output, and updates the database state.
- `backend/app/api/routes/websockets.py`: [NEW] A new WebSocket endpoint to manage connections per `document_id` and broadcast progress to clients.
- `backend/app/main.py`: Included the new WebSocket router.

## Risks
- **Supabase RPC vs Naive Polling**: Currently, `claim_next_job` is doing a naive `GET` + `PATCH` because we lack an explicit atomic `claim_next_job` PL/pgSQL function in Supabase. In a multi-worker environment, this can result in race conditions where two workers process the same job.
- **Worker Execution Environment**: You will need to run `python -m app.workers.queue_worker` as a separate background process alongside `uvicorn main:app`.

## Recommendations
- For production, I recommend creating a Supabase RPC for `claim_next_job` that does an atomic `UPDATE ... RETURNING`.
- Add an explicit runner script or Docker Compose setup to bring up both the API Server and the Worker side-by-side.

## Next Steps (Phase 3: AI & Citation Intelligence)
- Create the `ai_providers/` module to abstract Gemini and DeepSeek.
- Completely remove legacy `ollama_service.py`.
- Integrate Semantic Scholar alongside CrossRef and OpenAlex in the citation validation module.
