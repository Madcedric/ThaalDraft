-- 04_jobs.sql
CREATE TABLE IF NOT EXISTS public.jobs (
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
