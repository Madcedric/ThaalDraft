-- ============================================================
-- ThaalDraft V2 — Safe Deployment Script
-- Uses IF NOT EXISTS for all objects (idempotent)
-- Run against Supabase SQL Editor
-- ============================================================

-- Step 1: Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Step 2: Create helper function
CREATE OR REPLACE FUNCTION public.set_updated_at()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$;

-- Step 3: Create all tables (IF NOT EXISTS = safe to re-run)
-- Tables are in dependency order (parents before children)

-- Users
CREATE TABLE IF NOT EXISTS public.users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  full_name TEXT,
  display_name TEXT,
  photo_url TEXT,
  avatar_url TEXT,
  provider TEXT DEFAULT 'firebase',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
DROP TRIGGER IF EXISTS trg_users_updated_at ON public.users;
CREATE TRIGGER trg_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Documents
CREATE TABLE IF NOT EXISTS public.documents (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  original_filename TEXT,
  storage_path TEXT NOT NULL,
  file_type TEXT DEFAULT 'unknown',
  mode TEXT NOT NULL DEFAULT 'reconstruction',
  status TEXT NOT NULL DEFAULT 'uploaded',
  target_journal TEXT,
  selected_template TEXT,
  size_bytes BIGINT DEFAULT 0,
  file_size_bytes BIGINT,
  word_count INTEGER DEFAULT 0,
  title TEXT,
  parsed_json JSONB DEFAULT '{}',
  structured_json JSONB DEFAULT '{}',
  ai_classification JSONB DEFAULT '{}',
  citation_report JSONB DEFAULT '{}',
  compliance_report JSONB DEFAULT '{}',
  review_report JSONB DEFAULT '{}',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
DROP TRIGGER IF EXISTS trg_documents_updated_at ON public.documents;
CREATE TRIGGER trg_documents_updated_at BEFORE UPDATE ON public.documents FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON public.documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON public.documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_file_type ON public.documents(file_type);

-- Jobs (V1 compat)
CREATE TABLE IF NOT EXISTS public.jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  type TEXT NOT NULL,
  status TEXT DEFAULT 'pending',
  payload JSONB DEFAULT '{}',
  result JSONB DEFAULT '{}',
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Document Versions
CREATE TABLE IF NOT EXISTS public.document_versions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  version_number INTEGER NOT NULL DEFAULT 1,
  source_type TEXT NOT NULL,
  source_path TEXT,
  extracted_text TEXT,
  raw_json JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_document_versions_document_id ON public.document_versions(document_id);

-- Manuscripts (Canonical Model)
CREATE TABLE IF NOT EXISTS public.manuscripts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL UNIQUE REFERENCES public.documents(id) ON DELETE CASCADE,
  title TEXT,
  abstract TEXT,
  keywords TEXT[] NOT NULL DEFAULT '{}',
  canonical_json JSONB NOT NULL DEFAULT '{}',
  word_count INTEGER DEFAULT 0,
  section_count INTEGER DEFAULT 0,
  reference_count INTEGER DEFAULT 0,
  confidence_score NUMERIC(5,2) DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
DROP TRIGGER IF EXISTS trg_manuscripts_updated_at ON public.manuscripts;
CREATE TRIGGER trg_manuscripts_updated_at BEFORE UPDATE ON public.manuscripts FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Sections
CREATE TABLE IF NOT EXISTS public.sections (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  manuscript_id UUID NOT NULL REFERENCES public.manuscripts(id) ON DELETE CASCADE,
  heading TEXT NOT NULL,
  label TEXT NOT NULL,
  section_order INTEGER NOT NULL DEFAULT 0,
  level INTEGER NOT NULL DEFAULT 1,
  confidence NUMERIC(5,2) DEFAULT 0,
  content TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_sections_manuscript_id ON public.sections(manuscript_id);

-- Figures
CREATE TABLE IF NOT EXISTS public.figures (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  manuscript_id UUID NOT NULL REFERENCES public.manuscripts(id) ON DELETE CASCADE,
  figure_number TEXT,
  caption TEXT,
  image_path TEXT,
  image_mime_type TEXT,
  width INTEGER,
  height INTEGER,
  extracted_from TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_figures_manuscript_id ON public.figures(manuscript_id);

-- Tables
CREATE TABLE IF NOT EXISTS public."tables" (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  manuscript_id UUID NOT NULL REFERENCES public.manuscripts(id) ON DELETE CASCADE,
  table_number TEXT,
  caption TEXT,
  table_data JSONB NOT NULL DEFAULT '[]',
  extracted_from TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_tables_manuscript_id ON public."tables"(manuscript_id);

-- References
CREATE TABLE IF NOT EXISTS public.references_table (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  manuscript_id UUID NOT NULL REFERENCES public.manuscripts(id) ON DELETE CASCADE,
  ref_index INTEGER NOT NULL,
  raw_text TEXT NOT NULL,
  authors TEXT[],
  title TEXT,
  journal TEXT,
  year INTEGER,
  doi TEXT,
  url TEXT,
  citation_style TEXT,
  is_valid BOOLEAN DEFAULT true,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_references_manuscript_id ON public.references_table(manuscript_id);
CREATE INDEX IF NOT EXISTS idx_references_doi ON public.references_table(doi);

-- DOI Records
CREATE TABLE IF NOT EXISTS public.doi_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  reference_id UUID REFERENCES public.references_table(id) ON DELETE CASCADE,
  document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
  doi TEXT NOT NULL,
  source TEXT NOT NULL DEFAULT 'crossref',
  metadata JSONB NOT NULL DEFAULT '{}',
  resolved BOOLEAN NOT NULL DEFAULT false,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
DROP TRIGGER IF EXISTS trg_doi_records_updated_at ON public.doi_records;
CREATE TRIGGER trg_doi_records_updated_at BEFORE UPDATE ON public.doi_records FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_doi_records_doi ON public.doi_records(doi);

-- Citation Reports
CREATE TABLE IF NOT EXISTS public.citation_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL UNIQUE REFERENCES public.documents(id) ON DELETE CASCADE,
  report JSONB NOT NULL DEFAULT '{}',
  health_score NUMERIC(5,2) DEFAULT 0,
  citation_style TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
DROP TRIGGER IF EXISTS trg_citation_reports_updated_at ON public.citation_reports;
CREATE TRIGGER trg_citation_reports_updated_at BEFORE UPDATE ON public.citation_reports FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Compliance Reports
CREATE TABLE IF NOT EXISTS public.compliance_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL UNIQUE REFERENCES public.documents(id) ON DELETE CASCADE,
  journal_id TEXT NOT NULL,
  report JSONB NOT NULL DEFAULT '{}',
  compliance_score NUMERIC(5,2) DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
DROP TRIGGER IF EXISTS trg_compliance_reports_updated_at ON public.compliance_reports;
CREATE TRIGGER trg_compliance_reports_updated_at BEFORE UPDATE ON public.compliance_reports FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Review Reports
CREATE TABLE IF NOT EXISTS public.review_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL UNIQUE REFERENCES public.documents(id) ON DELETE CASCADE,
  analysis_method TEXT NOT NULL DEFAULT 'deterministic',
  report JSONB NOT NULL DEFAULT '{}',
  readiness_score NUMERIC(5,2) DEFAULT 0,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
DROP TRIGGER IF EXISTS trg_review_reports_updated_at ON public.review_reports;
CREATE TRIGGER trg_review_reports_updated_at BEFORE UPDATE ON public.review_reports FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();

-- Formatting Jobs
CREATE TABLE IF NOT EXISTS public.formatting_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  template_id TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  input_json JSONB NOT NULL DEFAULT '{}',
  output_json JSONB NOT NULL DEFAULT '{}',
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
DROP TRIGGER IF EXISTS trg_formatting_jobs_updated_at ON public.formatting_jobs;
CREATE TRIGGER trg_formatting_jobs_updated_at BEFORE UPDATE ON public.formatting_jobs FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_formatting_jobs_document_id ON public.formatting_jobs(document_id);

-- Exports
CREATE TABLE IF NOT EXISTS public.exports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  format TEXT NOT NULL,
  storage_path TEXT,
  file_name TEXT,
  status TEXT NOT NULL DEFAULT 'pending',
  download_url TEXT,
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
DROP TRIGGER IF EXISTS trg_exports_updated_at ON public.exports;
CREATE TRIGGER trg_exports_updated_at BEFORE UPDATE ON public.exports FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_exports_document_id ON public.exports(document_id);

-- Submission Packages
CREATE TABLE IF NOT EXISTS public.submission_packages (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  status TEXT NOT NULL DEFAULT 'pending',
  package_path TEXT,
  package_name TEXT,
  components JSONB NOT NULL DEFAULT '[]',
  metadata JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
DROP TRIGGER IF EXISTS trg_submission_packages_updated_at ON public.submission_packages;
CREATE TRIGGER trg_submission_packages_updated_at BEFORE UPDATE ON public.submission_packages FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_submission_packages_document_id ON public.submission_packages(document_id);

-- Batch Jobs
CREATE TABLE IF NOT EXISTS public.batch_jobs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  batch_name TEXT NOT NULL DEFAULT '',
  status TEXT NOT NULL DEFAULT 'pending',
  total_files INTEGER NOT NULL DEFAULT 0,
  completed_files INTEGER NOT NULL DEFAULT 0,
  failed_files INTEGER NOT NULL DEFAULT 0,
  payload JSONB NOT NULL DEFAULT '{}',
  result JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
DROP TRIGGER IF EXISTS trg_batch_jobs_updated_at ON public.batch_jobs;
CREATE TRIGGER trg_batch_jobs_updated_at BEFORE UPDATE ON public.batch_jobs FOR EACH ROW EXECUTE FUNCTION public.set_updated_at();
CREATE INDEX IF NOT EXISTS idx_batch_jobs_user_id ON public.batch_jobs(user_id);

-- Batch Files
CREATE TABLE IF NOT EXISTS public.batch_files (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  batch_job_id UUID NOT NULL REFERENCES public.batch_jobs(id) ON DELETE CASCADE,
  filename TEXT NOT NULL,
  status TEXT NOT NULL DEFAULT 'pending',
  file_size BIGINT,
  document_id UUID REFERENCES public.documents(id) ON DELETE SET NULL,
  error TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_batch_files_batch_job_id ON public.batch_files(batch_job_id);

-- Activity Logs
CREATE TABLE IF NOT EXISTS public.activity_logs (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT REFERENCES public.users(id) ON DELETE SET NULL,
  document_id UUID REFERENCES public.documents(id) ON DELETE CASCADE,
  action TEXT NOT NULL,
  entity_type TEXT,
  entity_id UUID,
  details JSONB NOT NULL DEFAULT '{}',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_activity_logs_document_id ON public.activity_logs(document_id);
CREATE INDEX IF NOT EXISTS idx_activity_logs_user_id ON public.activity_logs(user_id);

-- Journal Templates
CREATE TABLE IF NOT EXISTS public.journal_templates (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  column_count INTEGER NOT NULL DEFAULT 1,
  line_spacing NUMERIC(4,2) NOT NULL DEFAULT 1.0,
  reference_style TEXT NOT NULL,
  citation_style TEXT NOT NULL,
  section_style TEXT NOT NULL,
  page_size TEXT NOT NULL DEFAULT 'A4',
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
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

-- Custom Templates
CREATE TABLE IF NOT EXISTS public.custom_templates (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id TEXT NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
  template_id TEXT NOT NULL UNIQUE,
  template_name TEXT NOT NULL,
  template_config JSONB NOT NULL DEFAULT '{}',
  base_template_id TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_custom_templates_user_id ON public.custom_templates(user_id);

-- Plagiarism Checks (V1 compat)
CREATE TABLE IF NOT EXISTS public.plagiarism_checks (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  report JSONB DEFAULT '{}',
  similarity_score FLOAT DEFAULT 0.0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Citations (V1 compat)
CREATE TABLE IF NOT EXISTS public.citations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  document_id UUID NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  raw_text TEXT NOT NULL,
  type TEXT DEFAULT 'unknown',
  source_section TEXT DEFAULT '',
  reference_index INTEGER DEFAULT -1,
  is_resolved BOOLEAN DEFAULT false,
  confidence FLOAT DEFAULT 0.0,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- DONE — 20 tables created
-- ============================================================
