-- 08_add_structured_json.sql
ALTER TABLE public.documents
ADD COLUMN IF NOT EXISTS structured_json jsonb;
