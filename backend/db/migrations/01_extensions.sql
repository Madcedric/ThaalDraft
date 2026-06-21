-- 01_extensions.sql
-- Enable useful Postgres extensions
CREATE EXTENSION IF NOT EXISTS citext;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
-- If using uuid generation functions (Supabase has pgcrypto by default)
CREATE EXTENSION IF NOT EXISTS pgcrypto;
