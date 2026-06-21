-- ThaalDraft V2
-- Supabase PostgreSQL schema
-- Backend uses service role key; RLS is intentionally omitted for simplicity in V2.

create extension if not exists pgcrypto;

-- ============================================================
-- UPDATED_AT TRIGGER
-- ============================================================
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

-- ============================================================
-- USERS
-- ============================================================
create table if not exists public.users (
  id uuid primary key default gen_random_uuid(),
  firebase_uid text not null unique,
  email text,
  full_name text,
  provider text not null default 'firebase',
  photo_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_users_updated_at on public.users;
create trigger trg_users_updated_at
before update on public.users
for each row execute function public.set_updated_at();

-- ============================================================
-- DOCUMENTS
-- ============================================================
create table if not exists public.documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  filename text not null,
  original_filename text,
  file_type text not null,
  mode text not null default 'reconstruction',
  status text not null default 'uploaded',
  target_journal text,
  storage_path text,
  file_size_bytes bigint,
  word_count integer default 0,
  title text,
  parsed_json jsonb not null default '{}'::jsonb,
  structured_json jsonb not null default '{}'::jsonb,
  selected_template text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_documents_updated_at on public.documents;
create trigger trg_documents_updated_at
before update on public.documents
for each row execute function public.set_updated_at();

create index if not exists idx_documents_user_id on public.documents(user_id);
create index if not exists idx_documents_status on public.documents(status);
create index if not exists idx_documents_file_type on public.documents(file_type);
create index if not exists idx_documents_target_journal on public.documents(target_journal);

-- ============================================================
-- DOCUMENT VERSIONS
-- ============================================================
create table if not exists public.document_versions (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  version_number integer not null default 1,
  source_type text not null,
  source_path text,
  extracted_text text,
  raw_json jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_document_versions_document_id on public.document_versions(document_id);

-- ============================================================
-- MANUSCRIPTS (CANONICAL MODEL)
-- ============================================================
create table if not exists public.manuscripts (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null unique references public.documents(id) on delete cascade,
  title text,
  abstract text,
  keywords text[] not null default '{}',
  canonical_json jsonb not null default '{}'::jsonb,
  word_count integer default 0,
  section_count integer default 0,
  reference_count integer default 0,
  confidence_score numeric(5,2) default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_manuscripts_updated_at on public.manuscripts;
create trigger trg_manuscripts_updated_at
before update on public.manuscripts
for each row execute function public.set_updated_at();

-- ============================================================
-- SECTIONS
-- ============================================================
create table if not exists public.sections (
  id uuid primary key default gen_random_uuid(),
  manuscript_id uuid not null references public.manuscripts(id) on delete cascade,
  heading text not null,
  label text not null,
  section_order integer not null default 0,
  level integer not null default 1,
  confidence numeric(5,2) default 0,
  content text,
  created_at timestamptz not null default now()
);

create index if not exists idx_sections_manuscript_id on public.sections(manuscript_id);

-- ============================================================
-- FIGURES
-- ============================================================
create table if not exists public.figures (
  id uuid primary key default gen_random_uuid(),
  manuscript_id uuid not null references public.manuscripts(id) on delete cascade,
  figure_number text,
  caption text,
  image_path text,
  image_mime_type text,
  width integer,
  height integer,
  extracted_from text,
  created_at timestamptz not null default now()
);

create index if not exists idx_figures_manuscript_id on public.figures(manuscript_id);

-- ============================================================
-- TABLES
-- ============================================================
create table if not exists public.tables (
  id uuid primary key default gen_random_uuid(),
  manuscript_id uuid not null references public.manuscripts(id) on delete cascade,
  table_number text,
  caption text,
  table_data jsonb not null default '[]'::jsonb,
  extracted_from text,
  created_at timestamptz not null default now()
);

create index if not exists idx_tables_manuscript_id on public.tables(manuscript_id);

-- ============================================================
-- REFERENCES
-- ============================================================
create table if not exists public.references_table (
  id uuid primary key default gen_random_uuid(),
  manuscript_id uuid not null references public.manuscripts(id) on delete cascade,
  ref_index integer not null,
  raw_text text not null,
  authors text[],
  title text,
  journal text,
  year integer,
  doi text,
  url text,
  citation_style text,
  is_valid boolean default true,
  created_at timestamptz not null default now()
);

create index if not exists idx_references_manuscript_id on public.references_table(manuscript_id);
create index if not exists idx_references_doi on public.references_table(doi);

-- ============================================================
-- DOI RECORDS
-- ============================================================
create table if not exists public.doi_records (
  id uuid primary key default gen_random_uuid(),
  reference_id uuid references public.references_table(id) on delete cascade,
  document_id uuid references public.documents(id) on delete cascade,
  doi text not null,
  source text not null default 'crossref',
  metadata jsonb not null default '{}'::jsonb,
  resolved boolean not null default false,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_doi_records_updated_at on public.doi_records;
create trigger trg_doi_records_updated_at
before update on public.doi_records
for each row execute function public.set_updated_at();

create index if not exists idx_doi_records_doi on public.doi_records(doi);

-- ============================================================
-- CITATION REPORTS
-- ============================================================
create table if not exists public.citation_reports (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null unique references public.documents(id) on delete cascade,
  report jsonb not null default '{}'::jsonb,
  health_score numeric(5,2) default 0,
  citation_style text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_citation_reports_updated_at on public.citation_reports;
create trigger trg_citation_reports_updated_at
before update on public.citation_reports
for each row execute function public.set_updated_at();

-- ============================================================
-- COMPLIANCE REPORTS
-- ============================================================
create table if not exists public.compliance_reports (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null unique references public.documents(id) on delete cascade,
  journal_id text not null,
  report jsonb not null default '{}'::jsonb,
  compliance_score numeric(5,2) default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_compliance_reports_updated_at on public.compliance_reports;
create trigger trg_compliance_reports_updated_at
before update on public.compliance_reports
for each row execute function public.set_updated_at();

-- ============================================================
-- REVIEW REPORTS
-- ============================================================
create table if not exists public.review_reports (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null unique references public.documents(id) on delete cascade,
  analysis_method text not null default 'deterministic',
  report jsonb not null default '{}'::jsonb,
  readiness_score numeric(5,2) default 0,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_review_reports_updated_at on public.review_reports;
create trigger trg_review_reports_updated_at
before update on public.review_reports
for each row execute function public.set_updated_at();

-- ============================================================
-- FORMATTING JOBS
-- ============================================================
create table if not exists public.formatting_jobs (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  template_id text not null,
  status text not null default 'pending',
  input_json jsonb not null default '{}'::jsonb,
  output_json jsonb not null default '{}'::jsonb,
  error_message text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_formatting_jobs_updated_at on public.formatting_jobs;
create trigger trg_formatting_jobs_updated_at
before update on public.formatting_jobs
for each row execute function public.set_updated_at();

create index if not exists idx_formatting_jobs_document_id on public.formatting_jobs(document_id);

-- ============================================================
-- EXPORTS
-- ============================================================
create table if not exists public.exports (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  format text not null,
  storage_path text,
  file_name text,
  status text not null default 'pending',
  download_url text,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_exports_updated_at on public.exports;
create trigger trg_exports_updated_at
before update on public.exports
for each row execute function public.set_updated_at();

create index if not exists idx_exports_document_id on public.exports(document_id);

-- ============================================================
-- SUBMISSION PACKAGES
-- ============================================================
create table if not exists public.submission_packages (
  id uuid primary key default gen_random_uuid(),
  document_id uuid not null references public.documents(id) on delete cascade,
  status text not null default 'pending',
  package_path text,
  package_name text,
  components jsonb not null default '[]'::jsonb,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_submission_packages_updated_at on public.submission_packages;
create trigger trg_submission_packages_updated_at
before update on public.submission_packages
for each row execute function public.set_updated_at();

create index if not exists idx_submission_packages_document_id on public.submission_packages(document_id);

-- ============================================================
-- BATCH JOBS
-- ============================================================
create table if not exists public.batch_jobs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references public.users(id) on delete cascade,
  batch_name text not null,
  status text not null default 'pending',
  total_files integer not null default 0,
  completed_files integer not null default 0,
  failed_files integer not null default 0,
  payload jsonb not null default '{}'::jsonb,
  result jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

drop trigger if exists trg_batch_jobs_updated_at on public.batch_jobs;
create trigger trg_batch_jobs_updated_at
before update on public.batch_jobs
for each row execute function public.set_updated_at();

create index if not exists idx_batch_jobs_user_id on public.batch_jobs(user_id);

-- ============================================================
-- ACTIVITY LOGS
-- ============================================================
create table if not exists public.activity_logs (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references public.users(id) on delete set null,
  document_id uuid references public.documents(id) on delete cascade,
  action text not null,
  entity_type text,
  entity_id uuid,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists idx_activity_logs_document_id on public.activity_logs(document_id);
create index if not exists idx_activity_logs_user_id on public.activity_logs(user_id);

-- ============================================================
-- DEFAULT JOURNAL TEMPLATES
-- ============================================================
create table if not exists public.journal_templates (
  id text primary key,
  name text not null,
  description text,
  column_count integer not null default 1,
  line_spacing numeric(4,2) not null default 1.0,
  reference_style text not null,
  citation_style text not null,
  section_style text not null,
  page_size text not null default 'A4',
  created_at timestamptz not null default now()
);

insert into public.journal_templates
(id, name, description, column_count, line_spacing, reference_style, citation_style, section_style, page_size)
values
('ieee', 'IEEE', 'Two-column conference format', 2, 1.0, 'numeric', 'numeric', 'roman', 'LETTER'),
('elsevier', 'Elsevier', 'Harvard author-year journal format', 1, 1.5, 'harvard', 'author_year', 'arabic', 'A4'),
('springer', 'Springer', 'Lecture notes format', 1, 1.0, 'numeric', 'numeric', 'arabic', 'A4'),
('acm', 'ACM', 'ACM conference format', 2, 1.0, 'numeric', 'numeric', 'roman', 'LETTER'),
('apa', 'APA', 'APA 7th edition', 1, 2.0, 'apa', 'author_year', 'arabic', 'A4'),
('mla', 'MLA', 'MLA academic format', 1, 2.0, 'mla', 'author_page', 'arabic', 'A4'),
('nature', 'Nature', 'Nature journal format', 1, 1.0, 'numeric', 'numeric', 'arabic', 'A4')
on conflict (id) do nothing;