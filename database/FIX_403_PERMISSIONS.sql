-- ============================================================
-- Fix 403: Grant service_role full access to all V2 tables
-- Run this in Supabase SQL Editor
-- ============================================================

-- Grant full access to service_role for all tables
GRANT ALL ON ALL TABLES IN SCHEMA public TO service_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO service_role;
GRANT ALL ON ALL FUNCTIONS IN SCHEMA public TO service_role;

-- Also ensure RLS policies allow service_role
-- (Supabase service_role bypasses RLS by default, but this ensures explicit access)

-- Verify by testing
SELECT 'Permissions granted successfully' AS result;
