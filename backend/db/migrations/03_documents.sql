-- 03_documents.sql
CREATE TABLE IF NOT EXISTS public.documents (
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
