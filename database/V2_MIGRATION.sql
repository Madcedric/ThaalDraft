-- ============================================================
-- ThaalDraft V2 — Safe Migration Script
-- Run this AFTER V1 schema is already in Supabase
-- Uses ALTER TABLE to add missing columns/indexes
-- Safe to run multiple times (idempotent)
-- ============================================================

-- ============================================================
-- 1. USERS — V1 has id TEXT, V2 wants id UUID
--    We keep V1 TEXT id for backward compatibility
--    Just add missing columns
-- ============================================================
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS full_name text;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS photo_url text;

-- ============================================================
-- 2. DOCUMENTS — Add V2 columns to existing V1 table
-- ============================================================
ALTER TABLE public.documents ADD COLUMN IF NOT EXISTS original_filename text;
ALTER TABLE public.documents ADD COLUMN IF NOT EXISTS mode text NOT NULL DEFAULT 'reconstruction';
ALTER TABLE public.documents ADD COLUMN IF NOT EXISTS target_journal text;
ALTER TABLE public.documents ADD COLUMN IF NOT EXISTS file_size_bytes bigint;
ALTER TABLE public.documents ADD COLUMN IF NOT EXISTS word_count integer DEFAULT 0;
ALTER TABLE public.documents ADD COLUMN IF NOT EXISTS title text;
ALTER TABLE public.documents ADD COLUMN IF NOT EXISTS selected_template text;

-- Add V2 status values to the check constraint
-- (V1 has a CHECK constraint, V2 adds more statuses)
ALTER TABLE public.documents DROP CONSTRAINT IF EXISTS documents_status_check;
ALTER TABLE public.documents ADD CONSTRAINT documents_status_check
  CHECK (status IN (
    'uploaded', 'parsing', 'parsed', 'classifying', 'classified',
    'structuring', 'structured', 'formatting', 'formatted', 'failed',
    'reviewing', 'reviewed', 'compliant', 'non_compliant'
  ));

-- Add indexes (safe — IF NOT EXISTS)
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON public.documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON public.documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_file_type ON public.documents(file_type);
CREATE INDEX IF NOT EXISTS idx_documents_target_journal ON public.documents(target_journal);

-- ============================================================
-- 3. DOCUMENT VERSIONS — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.document_versions (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  version_number integer NOT NULL DEFAULT 1,
  source_type text NOT NULL,
  source_path text,
  extracted_text text,
  raw_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_document_versions_document_id ON public.document_versions(document_id);

-- ============================================================
-- 4. MANUSCRIPTS (CANONICAL MODEL) — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.manuscripts (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL UNIQUE REFERENCES public.documents(id) ON DELETE CASCADE,
  title text,
  abstract text,
  keywords text[] NOT NULL DEFAULT '{}',
  canonical_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  word_count integer DEFAULT 0,
  section_count integer DEFAULT 0,
  reference_count integer DEFAULT 0,
  confidence_score numeric(5,2) DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);

DROP TRIGGER IF EXISTS trg_manuscripts_updated_at ON public.manuscripts;
CREATE TRIGGER trg_manuscripts_updated_at
BEFORE UPDATE ON public.manuscripts
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ============================================================
-- 5. SECTIONS — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.sections (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  manuscript_id uuid NOT NULL REFERENCES public.manuscripts(id) ON DELETE CASCADE,
  heading text NOT NULL,
  label text NOT NULL,
  section_order integer NOT NULL DEFAULT 0,
  level integer NOT NULL DEFAULT 1,
  confidence numeric(5,2) DEFAULT 0,
  content text,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_sections_manuscript_id ON public.sections(manuscript_id);

-- ============================================================
-- 6. FIGURES — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.figures (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  manuscript_id uuid NOT NULL REFERENCES public.manuscripts(id) ON DELETE CASCADE,
  figure_number text,
  caption text,
  image_path text,
  image_mime_type text,
  width integer,
  height integer,
  extracted_from text,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_figures_manuscript_id ON public.figures(manuscript_id);

-- ============================================================
-- 7. TABLES — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.tables (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  manuscript_id uuid NOT NULL REFERENCES public.manuscripts(id) ON DELETE CASCADE,
  table_number text,
  caption text,
  table_data jsonb NOT NULL DEFAULT '[]'::jsonb,
  extracted_from text,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_tables_manuscript_id ON public.tables(manuscript_id);

-- ============================================================
-- 8. REFERENCES — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.references_table (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  manuscript_id uuid NOT NULL REFERENCES public.manuscripts(id) ON DELETE CASCADE,
  ref_index integer NOT NULL,
  raw_text text NOT NULL,
  authors text[],
  title text,
  journal text,
  year integer,
  doi text,
  url text,
  citation_style text,
  is_valid boolean DEFAULT true,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_references_manuscript_id ON public.references_table(manuscript_id);
CREATE INDEX IF NOT EXISTS idx_references_doi ON public.references_table(doi);

-- ============================================================
-- 9. DOI RECORDS — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.doi_records (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  reference_id uuid REFERENCES public.references_table(id) ON DELETE CASCADE,
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  doi text NOT NULL,
  source text NOT NULL DEFAULT 'crossref',
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  resolved boolean NOT NULL DEFAULT false,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS trg_doi_records_updated_at ON public.doi_records;
CREATE TRIGGER trg_doi_records_updated_at
BEFORE UPDATE ON public.doi_records
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_doi_records_doi ON public.doi_records(doi);

-- ============================================================
-- 10. CITATION REPORTS — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.citation_reports (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL UNIQUE REFERENCES public.documents(id) ON DELETE CASCADE,
  report jsonb NOT NULL DEFAULT '{}'::jsonb,
  health_score numeric(5,2) DEFAULT 0,
  citation_style text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS trg_citation_reports_updated_at ON public.citation_reports;
CREATE TRIGGER trg_citation_reports_updated_at
BEFORE UPDATE ON public.citation_reports
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ============================================================
-- 11. COMPLIANCE REPORTS — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.compliance_reports (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL UNIQUE REFERENCES public.documents(id) ON DELETE CASCADE,
  journal_id text NOT NULL,
  report jsonb NOT NULL DEFAULT '{}'::jsonb,
  compliance_score numeric(5,2) DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS trg_compliance_reports_updated_at ON public.compliance_reports;
CREATE TRIGGER trg_compliance_reports_updated_at
BEFORE UPDATE ON public.compliance_reports
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ============================================================
-- 12. REVIEW REPORTS — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.review_reports (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL UNIQUE REFERENCES public.documents(id) ON DELETE CASCADE,
  analysis_method text NOT NULL DEFAULT 'deterministic',
  report jsonb NOT NULL DEFAULT '{}'::jsonb,
  readiness_score numeric(5,2) DEFAULT 0,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS trg_review_reports_updated_at ON public.review_reports;
CREATE TRIGGER trg_review_reports_updated_at
BEFORE UPDATE ON public.review_reports
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- ============================================================
-- 13. FORMATTING JOBS — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.formatting_jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  template_id text NOT NULL,
  status text NOT NULL DEFAULT 'pending',
  input_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  output_json jsonb NOT NULL DEFAULT '{}'::jsonb,
  error_message text,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS trg_formatting_jobs_updated_at ON public.formatting_jobs;
CREATE TRIGGER trg_formatting_jobs_updated_at
BEFORE UPDATE ON public.formatting_jobs
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_formatting_jobs_document_id ON public.formatting_jobs(document_id);

-- ============================================================
-- 14. EXPORTS — Add V2 columns to existing V1 table
-- ============================================================
ALTER TABLE public.exports ADD COLUMN IF NOT EXISTS file_name text;
ALTER TABLE public.exports ADD COLUMN IF NOT EXISTS status text NOT NULL DEFAULT 'pending';
ALTER TABLE public.exports ADD COLUMN IF NOT EXISTS download_url text;
ALTER TABLE public.exports ADD COLUMN IF NOT EXISTS metadata jsonb NOT NULL DEFAULT '{}'::jsonb;
ALTER TABLE public.exports ADD COLUMN IF NOT EXISTS updated_at timestamptz NOT NULL DEFAULT now();

CREATE INDEX IF NOT EXISTS idx_exports_document_id ON public.exports(document_id);

-- ============================================================
-- 15. SUBMISSION PACKAGES — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.submission_packages (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id uuid NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  status text NOT NULL DEFAULT 'pending',
  package_path text,
  package_name text,
  components jsonb NOT NULL DEFAULT '[]'::jsonb,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS trg_submission_packages_updated_at ON public.submission_packages;
CREATE TRIGGER trg_submission_packages_updated_at
BEFORE UPDATE ON public.submission_packages
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_submission_packages_document_id ON public.submission_packages(document_id);

-- ============================================================
-- 16. BATCH JOBS — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.batch_jobs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  batch_name text NOT NULL DEFAULT '',
  status text NOT NULL DEFAULT 'pending',
  total_files integer NOT NULL DEFAULT 0,
  completed_files integer NOT NULL DEFAULT 0,
  failed_files integer NOT NULL DEFAULT 0,
  payload jsonb NOT NULL DEFAULT '{}'::jsonb,
  result jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now(),
  updated_at timestamptz NOT NULL DEFAULT now()
);
DROP TRIGGER IF EXISTS trg_batch_jobs_updated_at ON public.batch_jobs;
CREATE TRIGGER trg_batch_jobs_updated_at
BEFORE UPDATE ON public.batch_jobs
FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_batch_jobs_user_id ON public.batch_jobs(user_id);

-- ============================================================
-- 17. BATCH FILES — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.batch_files (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  batch_job_id uuid NOT NULL REFERENCES public.batch_jobs(id) ON DELETE CASCADE,
  filename text NOT NULL,
  status text NOT NULL DEFAULT 'pending',
  file_size bigint,
  document_id uuid REFERENCES public.documents(id) ON DELETE SET NULL,
  error text,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_batch_files_batch_job_id ON public.batch_files(batch_job_id);

-- ============================================================
-- 18. ACTIVITY LOGS — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.activity_logs (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid REFERENCES public.users(id) ON DELETE SET NULL,
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  action text NOT NULL,
  entity_type text,
  entity_id uuid,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_activity_logs_document_id ON public.activity_logs(document_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON public.activity_logs(user_id);

-- ============================================================
-- 19. JOURNAL TEMPLATES — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.journal_templates (
  id text PRIMARY KEY,
  name text NOT NULL,
  description text,
  column_count integer NOT NULL DEFAULT 1,
  line_spacing numeric(4,2) NOT NULL DEFAULT 1.0,
  reference_style text NOT NULL,
  citation_style text NOT NULL,
  section_style text NOT NULL,
  page_size text NOT NULL DEFAULT 'A4',
  created_at timestamptz NOT NULL DEFAULT now()
);

INSERT INTO public.journal_templates
(id, name, description, column_count, line_spacing, reference_style, citation_style, section_style, page_size)
VALUES
('ieee', 'IEEE', 'Two-column conference format', 2, 1.0, 'numeric', 'numeric', 'roman', 'LETTER'),
('elsevier', 'Elsevier', 'Harvard author-year journal format', 1, 1.5, 'harvard', 'author_year', 'arabic', 'A4'),
('springer', 'Springer', 'Lecture notes format', 1, 1.0, 'numeric', 'numeric', 'arabic', 'A4'),
('acm', 'ACM', 'ACM conference format', 2, 1.0, 'numeric', 'numeric', 'roman', 'LETTER'),
('apa', 'APA', 'APA 7th edition', 1, 2.0, 'apa', 'author_year', 'arabic', 'A4'),
('mla', 'MLA', 'MLA academic format', 1, 2.0, 'mla', 'author_page', 'arabic', 'A4'),
('nature', 'Nature', 'Nature journal format', 1, 1.0, 'numeric', 'numeric', 'arabic', 'A4')
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- 20. CUSTOM TEMPLATES — New V2 table
-- ============================================================
CREATE TABLE IF NOT EXISTS public.custom_templates (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  template_id text NOT NULL UNIQUE,
  template_name text NOT NULL,
  template_config jsonb NOT NULL DEFAULT '{}'::jsonb,
  base_template_id text,
  created_at timestamptz NOT NULL DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_custom_templates_user_id ON public.custom_templates(user_id);

-- ============================================================
-- DONE
-- ============================================================
