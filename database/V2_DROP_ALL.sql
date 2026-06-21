-- ============================================================
-- ThaalDraft V2 — DROP ALL + RECREATE
-- WARNING: This deletes ALL data in public schema
-- Run this first if previous schema runs failed
-- ============================================================

-- Drop all tables in correct order (respect foreign keys)
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- Grant permissions
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO anon;
GRANT ALL ON SCHEMA public TO authenticated;
GRANT ALL ON SCHEMA public TO service_role;

-- ============================================================
-- Now run V2_COMPLETE_SCHEMA.sql after this
-- ============================================================
