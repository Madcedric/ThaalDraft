-- 05_plagiarism_exports.sql
CREATE TABLE IF NOT EXISTS public.plagiarism_checks (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  report jsonb,
  similarity_score numeric,
  created_at timestamptz DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.exports (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  format text NOT NULL,
  storage_path text,
  created_at timestamptz DEFAULT now()
);
