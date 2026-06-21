-- 02_users.sql
CREATE TABLE IF NOT EXISTS public.users (
  id text PRIMARY KEY,
  email citext NOT NULL UNIQUE,
  name text,
  provider text NOT NULL DEFAULT 'firebase',
  created_at timestamptz DEFAULT now()
);
