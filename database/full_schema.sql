-- ThaalDraft Full Schema Migration
-- Idempotent: Safe to run multiple times
-- Run this directly in Supabase SQL Editor

-- ============================================================
-- EXTENSIONS
-- ============================================================
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- ============================================================
-- USERS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    provider TEXT DEFAULT 'firebase',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- DOCUMENTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    status TEXT DEFAULT 'uploaded' CHECK (status IN (
        'uploaded', 'parsing', 'parsed', 'classifying', 'classified',
        'structuring', 'structured', 'formatting', 'formatted', 'failed'
    )),
    size_bytes BIGINT DEFAULT 0,
    file_type TEXT DEFAULT 'unknown',
    parsed_json JSONB DEFAULT '{}',
    structured_json JSONB DEFAULT '{}',
    ai_classification JSONB DEFAULT '{}',
    citation_report JSONB DEFAULT '{}',
    compliance_report JSONB DEFAULT '{}',
    review_report JSONB DEFAULT '{}',
    selected_journal TEXT DEFAULT 'ieee',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- JOBS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN (
        'parse', 'classify', 'structure', 'format', 'plagiarism', 'citation', 'compliance', 'review'
    )),
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending', 'started', 'finished', 'failed'
    )),
    payload JSONB DEFAULT '{}',
    result JSONB DEFAULT '{}',
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- EXPORTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS exports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    format TEXT NOT NULL CHECK (format IN ('docx', 'pdf', 'latex')),
    storage_path TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- PLAGIARISM CHECKS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS plagiarism_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    report JSONB DEFAULT '{}',
    similarity_score FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- CITATIONS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS citations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    type TEXT DEFAULT 'unknown' CHECK (type IN ('numeric', 'author_year', 'unknown')),
    source_section TEXT DEFAULT '',
    reference_index INTEGER DEFAULT -1,
    is_resolved BOOLEAN DEFAULT FALSE,
    confidence FLOAT DEFAULT 0.0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- REFERENCES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS references_table (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    doi TEXT,
    authors JSONB DEFAULT '[]',
    title TEXT,
    year INTEGER,
    journal TEXT,
    volume TEXT,
    pages TEXT,
    cited_count INTEGER DEFAULT 0,
    is_cited BOOLEAN DEFAULT FALSE,
    is_valid_doi BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- COMPLIANCE REPORTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS compliance_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    journal_id TEXT NOT NULL,
    journal_name TEXT DEFAULT '',
    score JSONB DEFAULT '{}',
    issues JSONB DEFAULT '[]',
    checks_performed INTEGER DEFAULT 0,
    checks_passed INTEGER DEFAULT 0,
    checks_failed INTEGER DEFAULT 0,
    checks_warned INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- REVIEW REPORTS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS review_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    journal_id TEXT,
    strengths JSONB DEFAULT '[]',
    weaknesses JSONB DEFAULT '[]',
    missing_references JSONB DEFAULT '[]',
    improvement_suggestions JSONB DEFAULT '[]',
    category_scores JSONB DEFAULT '[]',
    publication_readiness JSONB DEFAULT '{}',
    total_findings INTEGER DEFAULT 0,
    critical_count INTEGER DEFAULT 0,
    major_count INTEGER DEFAULT 0,
    minor_count INTEGER DEFAULT 0,
    suggestion_count INTEGER DEFAULT 0,
    analysis_method TEXT DEFAULT 'deterministic',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- TEMPLATES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS templates (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    body_font JSONB DEFAULT '{}',
    title_font JSONB DEFAULT '{}',
    margins JSONB DEFAULT '{}',
    headings JSONB DEFAULT '[]',
    citation_style JSONB DEFAULT '{}',
    column_count INTEGER DEFAULT 1,
    line_spacing FLOAT DEFAULT 1.0,
    abstract_label TEXT DEFAULT 'Abstract',
    references_label TEXT DEFAULT 'References',
    two_column BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- BATCH JOBS TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS batch_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    job_type TEXT NOT NULL CHECK (job_type IN (
        'parse', 'classify', 'structure', 'format', 'citation', 'compliance', 'review'
    )),
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending', 'running', 'completed', 'failed', 'cancelled'
    )),
    total_files INTEGER DEFAULT 0,
    completed_files INTEGER DEFAULT 0,
    failed_files INTEGER DEFAULT 0,
    files JSONB DEFAULT '[]',
    payload JSONB DEFAULT '{}',
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- SUBMISSION PACKAGES TABLE
-- ============================================================
CREATE TABLE IF NOT EXISTS submission_packages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    journal_id TEXT NOT NULL,
    journal_name TEXT DEFAULT '',
    template_id TEXT DEFAULT '',
    status TEXT DEFAULT 'pending' CHECK (status IN (
        'pending', 'generating', 'completed', 'failed'
    )),
    components JSONB DEFAULT '[]',
    cover_letter JSONB DEFAULT '{}',
    author_statement JSONB DEFAULT '{}',
    conflict_statement JSONB DEFAULT '{}',
    zip_path TEXT,
    zip_size BIGINT,
    processing_metadata JSONB DEFAULT '{}',
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================
-- INDEXES
-- ============================================================
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at DESC);

CREATE INDEX IF NOT EXISTS idx_jobs_document_id ON jobs(document_id);
CREATE INDEX IF NOT EXISTS idx_jobs_status ON jobs(status);
CREATE INDEX IF NOT EXISTS idx_jobs_type ON jobs(type);

CREATE INDEX IF NOT EXISTS idx_exports_document_id ON exports(document_id);

CREATE INDEX IF NOT EXISTS idx_plagiarism_checks_document_id ON plagiarism_checks(document_id);

CREATE INDEX IF NOT EXISTS idx_citations_document_id ON citations(document_id);

CREATE INDEX IF NOT EXISTS idx_references_document_id ON references_table(document_id);

CREATE INDEX IF NOT EXISTS idx_compliance_reports_document_id ON compliance_reports(document_id);

CREATE INDEX IF NOT EXISTS idx_review_reports_document_id ON review_reports(document_id);

CREATE INDEX IF NOT EXISTS idx_batch_jobs_user_id ON batch_jobs(user_id);
CREATE INDEX IF NOT EXISTS idx_batch_jobs_status ON batch_jobs(status);

CREATE INDEX IF NOT EXISTS idx_submission_packages_document_id ON submission_packages(document_id);

-- ============================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE exports ENABLE ROW LEVEL SECURITY;
ALTER TABLE plagiarism_checks ENABLE ROW LEVEL SECURITY;
ALTER TABLE citations ENABLE ROW LEVEL SECURITY;
ALTER TABLE references_table ENABLE ROW LEVEL SECURITY;
ALTER TABLE compliance_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE review_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE templates ENABLE ROW LEVEL SECURITY;
ALTER TABLE batch_jobs ENABLE ROW LEVEL SECURITY;
ALTER TABLE submission_packages ENABLE ROW LEVEL SECURITY;

-- ============================================================
-- RLS POLICIES (Service role bypasses RLS, but policies exist for future use)
-- ============================================================

-- Users can read their own data
CREATE POLICY IF NOT EXISTS "Users can view own profile" ON users
    FOR SELECT USING (auth.uid() = id);

-- Users can manage their own documents
CREATE POLICY IF NOT EXISTS "Users can view own documents" ON documents
    FOR SELECT USING (user_id = auth.uid()::text);

CREATE POLICY IF NOT EXISTS "Users can insert own documents" ON documents
    FOR INSERT WITH CHECK (user_id = auth.uid()::text);

CREATE POLICY IF NOT EXISTS "Users can update own documents" ON documents
    FOR UPDATE USING (user_id = auth.uid()::text);

CREATE POLICY IF NOT EXISTS "Users can delete own documents" ON documents
    FOR DELETE USING (user_id = auth.uid()::text);

-- Users can manage their own jobs
CREATE POLICY IF NOT EXISTS "Users can view own jobs" ON jobs
    FOR SELECT USING (
        document_id IN (SELECT id FROM documents WHERE user_id = auth.uid()::text)
    );

-- Users can manage their own exports
CREATE POLICY IF NOT EXISTS "Users can view own exports" ON exports
    FOR SELECT USING (
        document_id IN (SELECT id FROM documents WHERE user_id = auth.uid()::text)
    );

-- Users can manage their own plagiarism checks
CREATE POLICY IF NOT EXISTS "Users can view own plagiarism checks" ON plagiarism_checks
    FOR SELECT USING (
        document_id IN (SELECT id FROM documents WHERE user_id = auth.uid()::text)
    );

-- Users can manage their own citations
CREATE POLICY IF NOT EXISTS "Users can view own citations" ON citations
    FOR SELECT USING (
        document_id IN (SELECT id FROM documents WHERE user_id = auth.uid()::text)
    );

-- Users can manage their own references
CREATE POLICY IF NOT EXISTS "Users can view own references" ON references_table
    FOR SELECT USING (
        document_id IN (SELECT id FROM documents WHERE user_id = auth.uid()::text)
    );

-- Users can manage their own compliance reports
CREATE POLICY IF NOT EXISTS "Users can view own compliance reports" ON compliance_reports
    FOR SELECT USING (
        document_id IN (SELECT id FROM documents WHERE user_id = auth.uid()::text)
    );

-- Users can manage their own review reports
CREATE POLICY IF NOT EXISTS "Users can view own review reports" ON review_reports
    FOR SELECT USING (
        document_id IN (SELECT id FROM documents WHERE user_id = auth.uid()::text)
    );

-- Templates are public read
CREATE POLICY IF NOT EXISTS "Templates are public" ON templates
    FOR SELECT USING (true);

-- Users can manage their own batch jobs
CREATE POLICY IF NOT EXISTS "Users can view own batch jobs" ON batch_jobs
    FOR SELECT USING (user_id = auth.uid()::text);

-- Users can manage their own submission packages
CREATE POLICY IF NOT EXISTS "Users can view own submission packages" ON submission_packages
    FOR SELECT USING (
        document_id IN (SELECT id FROM documents WHERE user_id = auth.uid()::text)
    );

-- ============================================================
-- INSERT DEFAULT TEMPLATES
-- ============================================================
INSERT INTO templates (id, name, description, column_count, line_spacing, abstract_label, references_label, two_column)
VALUES
    ('ieee', 'IEEE', 'Two-column technical format for engineering and computer science', 2, 1.0, 'Abstract', 'References', true),
    ('acm', 'ACM', 'Computer science conference proceedings format', 2, 1.0, 'Abstract', 'References', true),
    ('springer', 'Springer LNCS', 'Lecture Notes in Computer Science format', 2, 1.0, 'Abstract', 'References', true),
    ('elsevier', 'Elsevier', 'Scientific journal format for Elsevier publications', 1, 1.5, 'Abstract', 'References', false),
    ('apa', 'APA 7th Edition', 'American Psychological Association formatting standard', 1, 2.0, 'Abstract', 'References', false),
    ('mla', 'MLA 9th Edition', 'Modern Language Association humanities formatting', 1, 2.0, 'Abstract', 'Works Cited', false),
    ('nature', 'Nature', 'Single-column scientific journal format', 1, 1.5, 'Abstract', 'References', false)
ON CONFLICT (id) DO NOTHING;

-- ============================================================
-- DONE
-- ============================================================
