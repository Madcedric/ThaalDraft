-- DATABASE_SCHEMA_V2.sql
-- ThaalDraft V2 Database Schema Proposal

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY, -- Firebase UID
    email TEXT UNIQUE NOT NULL,
    provider TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Documents Table
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    filename TEXT NOT NULL,
    storage_path TEXT NOT NULL,
    mode TEXT NOT NULL DEFAULT 'reconstruction',
    target_journal TEXT,
    status TEXT NOT NULL DEFAULT 'uploaded',
    size_bytes BIGINT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Ensure V2 columns exist if the table was already created
ALTER TABLE documents ADD COLUMN IF NOT EXISTS mode TEXT DEFAULT 'reconstruction';
ALTER TABLE documents ADD COLUMN IF NOT EXISTS target_journal TEXT;

-- 3. Manuscripts (Normalized from JSONB)
CREATE TABLE IF NOT EXISTS manuscripts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    title TEXT,
    abstract TEXT,
    authors JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Sections
CREATE TABLE IF NOT EXISTS sections (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manuscript_id UUID NOT NULL REFERENCES manuscripts(id) ON DELETE CASCADE,
    heading TEXT,
    content TEXT,
    order_index INT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. References / Citations
CREATE TABLE IF NOT EXISTS references_table (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manuscript_id UUID NOT NULL REFERENCES manuscripts(id) ON DELETE CASCADE,
    raw_text TEXT NOT NULL,
    doi TEXT,
    authors JSONB,
    year INT,
    title TEXT,
    venue TEXT,
    is_valid BOOLEAN DEFAULT FALSE,
    validation_source TEXT -- CrossRef, OpenAlex, SemanticScholar
);

-- 6. Background Jobs
CREATE TABLE IF NOT EXISTS batch_jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    job_type TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'queued', -- queued, running, completed, failed
    result JSONB,
    error_message TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
