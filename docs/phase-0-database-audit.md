# Phase 0 — Database Audit

**Audit Date:** June 16, 2026
**Scope:** Supabase PostgreSQL schema, migrations, and data integrity

---

## Current Schema

### Tables

| Table | Columns | Purpose |
|---|---|---|
| `users` | id (text PK), email (citext UNIQUE), name, provider, created_at | Firebase auth user records |
| `documents` | id (uuid PK), user_id (FK), filename, storage_path, status, parsed_json (jsonb), ai_classification (jsonb), structured_json (jsonb), size_bytes, created_at, updated_at | Core document entity |
| `jobs` | id (uuid PK), document_id (FK), type, status, payload (jsonb), result (jsonb), created_at, started_at, finished_at | Async processing queue |
| `plagiarism_checks` | id (uuid PK), document_id (FK), report (jsonb), similarity_score (numeric), created_at | Plagiarism analysis results |
| `exports` | id (uuid PK), document_id (FK), format, storage_path, created_at | Generated export records |

### Extensions

| Extension | Purpose |
|---|---|
| `citext` | Case-insensitive text for email uniqueness |
| `pg_trgm` | Trigram fuzzy search on plagiarism reports |
| `pgcrypto` | UUID generation via `gen_random_uuid()` |

### Indexes

| Index | Table | Type | Purpose |
|---|---|---|---|
| `idx_documents_parsed_json` | documents | GIN | JSONB queries on parsed content |
| `idx_documents_user_id` | documents | B-tree | User document lookups |
| `idx_jobs_status` | jobs | B-tree | Job queue status filtering |
| `idx_plagiarism_report_trgm` | plagiarism_checks | GIN trigram | Fuzzy text search on reports |

### RLS Policies

| Policy | Table | Scope |
|---|---|---|
| `documents_owner` | documents | Direct ownership via `user_id = auth.uid()` |
| `jobs_owner` | jobs | Ownership via document join |
| `exports_owner` | exports | Ownership via document join |
| `plagiarism_owner` | plagiarism_checks | Ownership via document join |

---

## Missing Entities

### Critical

| Entity | Purpose | PRD Reference |
|---|---|---|
| `projects` | Group manuscripts into research projects | Module 1 (Document Processing) |
| `citations` | Individual citation records extracted from manuscripts | Module 3 (Citation Intelligence) |
| `references` | Individual reference/bibliography entries | Module 3 (Citation Intelligence) |
| `compliance_reports` | Journal compliance validation results | Module 5 (Journal Compliance) |
| `review_reports` | AI reviewer feedback results | Module 6 (Reviewer AI) |

### High

| Entity | Purpose | PRD Reference |
|---|---|---|
| `subscriptions` | SaaS subscription tier tracking | SaaS requirement |
| `usage_logs` | API usage and storage tracking | SaaS requirement |
| `templates` | Available formatting templates (IEEE, APA, etc.) | Module 7 (Formatting) |
| `batch_jobs` | Multi-file batch processing groups | Module 8 (Batch Processing) |

### Medium

| Entity | Purpose | PRD Reference |
|---|---|---|
| `cover_letters` | Generated cover letters | Module 9 (Submission Package) |
| `notifications` | User notifications for async operations | SaaS UX requirement |
| `audit_log` | User action history for compliance | Security requirement |

---

## Migration Requirements

### Critical Fixes

| ID | Migration | Issue | Fix |
|---|---|---|---|
| MIG-01 | `03_documents.sql` | `user_id` allows NULL | Add `NOT NULL` constraint |
| MIG-02 | `07_rls_policies.sql` | `CREATE POLICY IF NOT EXISTS` invalid syntax | Wrap in `DO` block for idempotency |
| MIG-03 | `07_rls_policies.sql` | RLS uses `auth.uid()` but app uses Firebase Auth | Decide: bypass RLS with service-role OR use Supabase Auth |

### High Priority

| ID | Migration | Purpose |
|---|---|---|
| MIG-04 | New migration | Add `subscriptions` table for SaaS tier tracking |
| MIG-05 | New migration | Add `citations` and `references` tables |
| MIG-06 | New migration | Add `compliance_reports` table |
| MIG-07 | New migration | Add `review_reports` table |
| MIG-08 | New migration | Add missing indexes on `jobs.document_id`, `plagiarism_checks.document_id`, `exports.document_id` |

### Medium Priority

| ID | Migration | Purpose |
|---|---|---|
| MIG-09 | `02_users.sql` | Add `subscription_tier`, `storage_quota_bytes`, `api_calls_count`, `is_active` columns |
| MIG-10 | `03_documents.sql` | Add `CHECK` constraint on `status` column |
| MIG-11 | `04_jobs.sql` | Add `retry_count`, `max_retries`, `locked_by`, `priority` columns |
| MIG-12 | New migration | Add `templates` table with IEEE, APA, MLA, ACM, Springer, Elsevier entries |

---

## Data Integrity Issues

| Issue | Table | Severity | Description |
|---|---|---|---|
| No `user_id` NOT NULL | documents | HIGH | Documents can exist without owner; breaks multi-tenancy |
| No status CHECK constraint | documents | MEDIUM | Any string accepted as status; no validation |
| No job_type CHECK constraint | jobs | MEDIUM | Any string accepted as job type |
| No email format check | users | LOW | `citext` allows any string as email |
| No file size validation | documents | LOW | `size_bytes` has no range constraint |
| RLS bypass with service-role | all | HIGH | Backend uses `SUPABASE_SERVICE_ROLE_KEY` which bypasses all RLS policies |
| `auth.uid()` mismatch | all | HIGH | RLS assumes Supabase Auth but app uses Firebase Auth; `auth.uid()` will never match Firebase UIDs |

---

## Summary

| Category | Critical | High | Medium | Low |
|---|---|---|---|---|
| Missing Entities | 5 | 4 | 3 | 0 |
| Migration Fixes | 3 | 5 | 4 | 0 |
| Data Integrity | 0 | 3 | 2 | 2 |
| **Total** | **8** | **12** | **9** | **2** |

**Overall Assessment:** The database schema covers core document processing but is missing 5 critical tables required by the PRD (projects, citations, references, compliance_reports, review_reports). The RLS policies are designed for Supabase Auth but the app uses Firebase Auth, making them ineffective. The `user_id` NULL issue in documents breaks multi-tenancy entirely.
