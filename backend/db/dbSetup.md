Adding DB integration tasks to the Phase 2 todo list.

Completed: _Add auth route `/me` to sync user_ (3/10)

Short answer: yes — you should provision a Supabase Postgres DB and create a small set of tables now. Below are the recommended steps, a concise ER overview, and starter SQL you can run (via Supabase SQL editor or migrations). After you review, I can create migration files and wire the backend env vars.

Steps (high level)

- Provision Supabase project (or Postgres) and a Storage bucket.
- Add `SUPABASE_URL`, `SUPABASE_KEY` (anon) and `SUPABASE_SERVICE_ROLE_KEY` (server) to `backend/.env`.
- Create DB extensions: `citext` and `pg_trgm`.
- Create core tables: `users`, `documents`, `jobs`, `plagiarism_checks`, `exports`.
- Add indexes (GIN for JSONB, trgm for similarity).
- Add RLS policies so users can access their rows; use service role key for server-side admin ops.
- Store migration SQL under `backend/db/migrations/` and track in Git.

ER overview (concise)

- `users` (1) —< `documents` (many) — `jobs` (many jobs per document)
- `documents` —(1)--> `plagiarism_checks` (many)
- `documents` —(1)--> `exports` (many)  
  Use `users.id` (text) as FK on `documents.user_id`. `documents.parsed_json` and AI outputs stored as `jsonb`.

Starter SQL (run in Supabase SQL editor or migrations)

- Extensions:
  CREATE EXTENSION IF NOT EXISTS citext;
  CREATE EXTENSION IF NOT EXISTS pg_trgm;

- Users:
  CREATE TABLE public.users (
  id text PRIMARY KEY,
  email citext NOT NULL UNIQUE,
  name text,
  provider text NOT NULL DEFAULT 'firebase',
  created_at timestamptz DEFAULT now()
  );

- Documents:
  CREATE TABLE public.documents (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id text REFERENCES public.users(id) ON DELETE CASCADE,
  filename text,
  storage_path text,
  status text DEFAULT 'uploaded',
  parsed_json jsonb,
  ai_classification jsonb,
  size_bytes int,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
  );

- Jobs (processing tasks):
  CREATE TABLE public.jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  type text NOT NULL,
  status text NOT NULL DEFAULT 'pending',
  payload jsonb,
  result jsonb,
  created_at timestamptz DEFAULT now(),
  started_at timestamptz,
  finished_at timestamptz
  );

- Plagiarism checks:
  CREATE TABLE public.plagiarism_checks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  report jsonb,
  similarity_score numeric,
  created_at timestamptz DEFAULT now()
  );

- Exports (DOCX/PDF artifacts metadata):
  CREATE TABLE public.exports (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  format text NOT NULL, -- 'docx' or 'pdf'
  storage_path text,
  created_at timestamptz DEFAULT now()
  );

Indexes

- GIN on JSONB:
  CREATE INDEX ON public.documents USING gin (parsed_json);
- Trigram for fast similarity (plagiarism):
  CREATE INDEX ON public.plagiarism_checks USING gin ((report->>'text')) WITH (gin_trgm_ops);
- Helpful indexes:
  CREATE INDEX ON public.documents (user_id);
  CREATE INDEX ON public.jobs (status);

Row Level Security (RLS) guidance

- Enable RLS on tables that store user data (`documents`, `jobs`, `exports`, `plagiarism_checks`).
- Create policies allowing the authenticated user to SELECT/INSERT/UPDATE on rows where `user_id = auth.uid()` (or use Supabase's `auth.uid()`), and allow server service role to bypass RLS for admin tasks. Example flow:
  - For frontend calls use anon key + RLS policies so users can only touch their rows.
  - For backend admin tasks (uploads, formatting), use `SUPABASE_SERVICE_ROLE_KEY`.

Migrations & tooling

- Option A: Use Supabase SQL editor to run these and export migrations.
- Option B: Add SQL files to `backend/db/migrations/` and apply via CI or `supabase` CLI / `psql`. I can create these files for you.

Backend changes (what to configure)

- Add `SUPABASE_SERVICE_ROLE_KEY` to `backend/.env` (not committed).
- Use the service role key only server-side for inserts/reads that require admin scope; keep client calls to public anon key plus RLS.

Security & production notes

- Never expose the service role key in the frontend.
- Add rate-limiting on AI and plagiarism endpoints.
- Add audit columns (`created_by`, `updated_by`) if you want traceability.

Would you like me to:

- create the SQL migration files under `backend/db/migrations/` now and wire .env.example with `SUPABASE_SERVICE_ROLE_KEY`, or
- just provide the SQL files for you to run manually?

Which should I do next?
