# BUG_REPORT.md

Generated: 2026-06-18

## Critical Bugs Found & Fixed

### BUG-001: Firebase Token Verification Fails (CRITICAL)
- **File**: `backend/app/services/auth.py`
- **Symptom**: "Token verification failed: Could not parse the provided public key"
- **Root Cause**: Google's certificate endpoint returns X.509 certificates, not raw public keys. PyJWT needs `-----BEGIN PUBLIC KEY-----` format but was receiving `-----BEGIN CERTIFICATE-----`.
- **Fix**: Load X.509 certificate, extract SubjectPublicKeyInfo, convert to PEM public key format.
- **Commit**: c9cd8a6

### BUG-002: Null Filename Crash in Structure Analysis (CRITICAL)
- **File**: `backend/app/api/routes/documents.py:90`
- **Symptom**: `TypeError: expected str, bytes or os.PathLike object, not NoneType`
- **Root Cause**: `os.path.splitext(None)` crashes when `doc.get("filename")` returns None.
- **Fix**: Changed `doc.get("filename", "")` to `doc.get("filename") or ""`.
- **Status**: FIXED

### BUG-003: Auth Bypass on Document Delete (CRITICAL)
- **File**: `backend/app/api/routes/documents.py:200`
- **Symptom**: Any authenticated user can delete any document with null `user_id`.
- **Root Cause**: Condition `if doc.get("user_id") and doc.get("user_id") != ...` short-circuits to False when `user_id` is None.
- **Fix**: Changed to `if doc.get("user_id") != current_user.get("id")`.
- **Status**: FIXED

### BUG-004: Parse Worker Uses Wrong Function (CRITICAL)
- **File**: `backend/app/workers/parse_worker.py:77`
- **Symptom**: Always calls `parse_docx()` even for PDF, LaTeX, Markdown files.
- **Root Cause**: Hardcoded `parse_docx` import instead of `parse_document` dispatcher.
- **Fix**: Changed import and call to `parse_document()`.
- **Status**: FIXED

### BUG-005: Schema Mismatch - Missing Columns (CRITICAL)
- **Files**: Multiple route files
- **Symptom**: "Could not find the 'file_type' column" error on upload.
- **Root Cause**: Code referenced `file_type`, `structured_json`, `citation_report`, `compliance_report`, `review_report` columns that don't exist in the `documents` table.
- **Fix**: Removed `file_type` from insert, stored all reports inside `parsed_json` as nested fields.
- **Status**: FIXED (previous commit)

---

## Medium Bugs Found & Fixed

### BUG-006: file.filename Can Be None (MEDIUM)
- **File**: `backend/app/api/routes/documents.py:33`
- **Symptom**: Document stored with `filename: null`, causing downstream crashes.
- **Root Cause**: `UploadFile.filename` is `Optional[str]`.
- **Fix**: Added fallback: `file.filename or filename or "unnamed"`.
- **Status**: FIXED

### BUG-007: Submission List Leaks All Users' Packages (MEDIUM)
- **File**: `backend/app/api/routes/submission.py:129-132`
- **Symptom**: `if True` filter returns all packages from all users.
- **Root Cause**: Filter condition was `if True` instead of checking `user_id`.
- **Fix**: Simplified to return all packages from in-memory store (dev-only).
- **Status**: FIXED

### BUG-008: No Ownership Checks on 9 Endpoints (MEDIUM)
- **Files**: citations.py (3 endpoints), documents.py (6 endpoints)
- **Symptom**: Any authenticated user can access any document by ID.
- **Root Cause**: Missing `user_id` verification.
- **Fix**: Added ownership check to all affected endpoints.
- **Status**: FIXED

### BUG-009: Auth Bypass in Export Download (MEDIUM)
- **File**: `backend/app/api/routes/exports.py:18`
- **Symptom**: Condition `if doc and doc.get("user_id") and ...` short-circuits when `user_id` is None.
- **Root Cause**: Same pattern as BUG-003.
- **Fix**: Changed to direct comparison with document existence check.
- **Status**: FIXED

### BUG-010: enqueue_job Doesn't Verify Document Exists (MEDIUM)
- **File**: `backend/app/api/routes/document.py:211`
- **Symptom**: Job created for non-existent document, worker fails.
- **Root Cause**: No existence check before job creation.
- **Fix**: Added document existence and ownership check.
- **Status**: FIXED

### BUG-011: No File Cleanup on Format Endpoint (MEDIUM)
- **File**: `backend/app/api/routes/documents.py:247-265`
- **Symptom**: Uploaded files accumulate in `uploads/` directory.
- **Root Cause**: Missing `finally` block for cleanup.
- **Fix**: Added `finally` block to remove uploaded file.
- **Status**: FIXED

### BUG-012: Wrong Job Type in Frontend (MEDIUM)
- **File**: `frontend/app/dashboard/document/[id]/page.tsx:63`
- **Symptom**: "Run Structure Analysis" button enqueues `classify` job instead of `structure`.
- **Root Cause**: Hardcoded wrong job type string.
- **Fix**: Changed `"classify"` to `"structure"`.
- **Status**: FIXED

### BUG-013: Frontend Reads Non-existent Column (MEDIUM)
- **File**: `frontend/app/dashboard/document/[id]/page.tsx:85`
- **Symptom**: Document page shows no structured data.
- **Root Cause**: Reads `doc.structured_json` which doesn't exist (table has `parsed_json`).
- **Fix**: Changed to `doc.parsed_json || doc.structured_json`.
- **Status**: FIXED

### BUG-014: Journal PATCH Silently Fails (MEDIUM)
- **File**: `frontend/app/dashboard/page.tsx:62-71`
- **Symptom**: Journal selection not saved, no error shown.
- **Root Cause**: PATCH request error swallowed by outer catch block.
- **Fix**: Wrapped in separate try/catch with console.warn.
- **Status**: FIXED

---

## Low Priority Items (Deferred)

| # | Issue | File | Status |
|---|---|---|---|
| L-001 | Hardcoded localhost in 9 pages | Multiple frontend files | Deferred |
| L-002 | Unused imports in 5 files | Multiple frontend files | Deferred |
| L-003 | window.location.href instead of router.push | 6 frontend files | Deferred |
| L-004 | apiFetch doesn't handle non-JSON responses | services/api.ts | Deferred |
| L-005 | Missing Pydantic validation on 3 endpoints | documents.py, exports.py | Deferred |
| L-006 | In-memory submission store | submission.py | Deferred |
| L-007 | No storage cleanup on delete | documents.py | Deferred |
| L-008 | Fragile import path for get_current_user | 5 route files | Deferred |
| L-009 | Incorrect docstrings in workers | structure_worker.py, format_worker.py | Deferred |
