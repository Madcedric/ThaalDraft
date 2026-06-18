# Environment Audit Report

Generated: 2026-06-18

## Summary

Environment variables have been audited, reorganized, and verified across both frontend and backend.

## Backend Environment Variables

### Required (used in code)

| Variable | Used In | Purpose |
|---|---|---|
| `SUPABASE_URL` | document_service, export_service, job_service, plagiarism_service, storage_service, user_service | Supabase project URL for REST API |
| `SUPABASE_SERVICE_ROLE_KEY` | document_service, export_service, job_service, plagiarism_service, storage_service, user_service | Supabase service role key for server-side operations |
| `SUPABASE_STORAGE_BUCKET` | storage_service | Supabase storage bucket name (default: "manuscripts") |
| `FIREBASE_PROJECT_ID` | auth.py | Firebase project ID for JWT verification |

### Files

| File | Status |
|---|---|
| `backend/.env` | Created with real values |
| `backend/.env.example` | Created with placeholder values |
| `backend/requirements.txt` | Updated with `python-dotenv>=1.0.0` |
| `backend/app/main.py` | Added `load_dotenv()` at startup |

## Frontend Environment Variables

### Required (used in code)

| Variable | Used In | Purpose |
|---|---|---|
| `NEXT_PUBLIC_API_BASE` | api.ts, helpers.ts, all dashboard pages | Backend API URL |
| `NEXT_PUBLIC_FIREBASE_API_KEY` | firebase.ts | Firebase client config |
| `NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN` | firebase.ts | Firebase client config |
| `NEXT_PUBLIC_FIREBASE_PROJECT_ID` | firebase.ts | Firebase client config |
| `NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET` | firebase.ts | Firebase client config |
| `NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID` | firebase.ts | Firebase client config |
| `NEXT_PUBLIC_FIREBASE_APP_ID` | firebase.ts | Firebase client config |

### Files

| File | Status |
|---|---|
| `frontend/.env` | Cleaned - only NEXT_PUBLIC_* vars |
| `frontend/.env.local.example` | Created with placeholder values |

## Removed from Frontend .env

These variables were in `frontend/.env` but belong only in `backend/.env`:

| Variable | Risk | Action |
|---|---|---|
| `DATABASE_URL` | **CRITICAL** - Contains DB password exposed to browser | Moved to backend |
| `SUPABASE_SERVICE_ROLE_KEY` | **CRITICAL** - Admin key exposed to browser | Moved to backend |
| `SUPABASE_URL` | Medium - Backend-only config | Moved to backend |
| `SUPABASE_KEY` | Medium - Duplicate of service role key | Removed |
| `SUPABASE_STORAGE_BUCKET` | Low - Backend-only config | Moved to backend |
| `OPENAI_API_KEY` | **CRITICAL** - API key not used in any code | Removed |
| `STORAGE_TYPE` | Low - Not used in any code | Removed |
| `FIREBASE_CLIENT_ID` | Low - Not used in frontend code | Removed |
| `FIREBASE_CLIENT_EMAIL` | Low - Backend-only (not used) | Removed |
| `FIREBASE_PROJECT_ID` (non-public) | Low - Frontend uses NEXT_PUBLIC_ version | Removed |

## Verification

### Backend Env Loading
```
SUPABASE_URL: OK (https://rjyzbgwudddievqagcpl.s...)
SUPABASE_SERVICE_ROLE_KEY: OK (eyJhbGciOiJIUzI1NiIsInR5cCI6Ik...)
SUPABASE_STORAGE_BUCKET: OK (thaaldraft)
FIREBASE_PROJECT_ID: OK (thaaldraft)
```

### Frontend Env Loading
All `NEXT_PUBLIC_*` variables present in `.env`.

## CORS Configuration

Updated `backend/app/main.py` to allow:
- `http://localhost:3000` (development)
- `https://thaaldraft.vercel.app` (production)
- `https://thaaldraft-git-main.vercel.app` (production preview)
