-- 06_indexes.sql
-- GIN index for JSONB parsed payloads
CREATE INDEX IF NOT EXISTS idx_documents_parsed_json ON public.documents USING gin (parsed_json);

-- Indexes for common lookups
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON public.documents (user_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON public.jobs (status);

-- Trigram index to support fuzzy similarity on plagiarism report text
-- Store textual reports under report->>'text' when running checks
CREATE INDEX IF NOT EXISTS idx_plagiarism_report_trgm ON public.plagiarism_checks USING gin ((report->>'text') gin_trgm_ops);
