-- Migration: Add display_name and avatar_url to users table
-- Run this if you already deployed V2_DEPLOY.sql

ALTER TABLE public.users ADD COLUMN IF NOT EXISTS display_name TEXT;
ALTER TABLE public.users ADD COLUMN IF NOT EXISTS avatar_url TEXT;

-- Update ensure_user_exists to handle new columns
-- (no code change needed, existing rows just get NULL)
