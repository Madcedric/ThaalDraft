# FIX_REPORT.md — Database Integration Fixes

**Date:** June 19, 2026
**Total Fixes:** 2 files changed
**Verification:** 16/16 E2E tests pass

---

## Fix 1: `backend/app/services/document_service.py`

### Change: Add `ensure_user_exists()` function

**Problem:** Real Firebase users don't exist in `users` table. FK constraint blocks document insert.

**Solution:** New function that creates user row in `users` table before document insert (idempotent).

```python
def ensure_user_exists(user_id: str, email: str = "") -> bool:
    """Ensure a user row exists in Supabase. Creates it if missing."""
    # Check if user exists
    r = requests.get(f"{url}?id=eq.{user_id}&select=id", ...)
    if r.json():
        return True  # Already exists

    # Insert user (upsert to avoid duplicate errors)
    r = requests.post(url, json=[{"id": user_id, "email": email, "provider": "firebase"}], ...)
    return r.status_code in (200, 201)
```

### Change: Add `_supabase_headers()` helper

**Problem:** Duplicated header construction across all functions.

**Solution:** Single helper function for consistent header construction.

```python
def _supabase_headers(include_return: bool = False) -> Dict:
    h = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    if include_return:
        h["Content-Type"] = "application/json"
        h["Prefer"] = "return=representation"
    return h
```

### Change: Add diagnostic logging to `create_document_record()`

**Problem:** Silent failures when Supabase insert fails (fallback UUID masks the error).

**Solution:** Log every step of the insert process.

```python
print(f"DB INSERT: user_id={doc.get('user_id')}, filename={doc.get('filename')}")
res = requests.post(url, json=[doc], headers=headers, timeout=15)
print(f"DB INSERT RESPONSE: status={res.status_code}")
if res.status_code in (200, 201):
    print(f"DB INSERT SUCCESS: id={created.get('id')}")
else:
    print(f"DB INSERT FAILED: {res.status_code} {res.text[:300]}")
# Fallback:
print(f"DB INSERT FALLBACK: id={fallback_id} (row NOT in database)")
```

### Change: Add diagnostic logging to `get_document()`

**Solution:** Log retrieval results for debugging.

```python
print(f"DB GET: document_id={document_id} FOUND, user_id={data[0].get('user_id')}")
# or
print(f"DB GET: document_id={document_id} NOT FOUND (empty result)")
```

---

## Fix 2: `backend/app/api/routes/documents.py`

### Change: Call `ensure_user_exists()` before document insert

**Problem:** Document insert fails because user doesn't exist in `users` table.

**Solution:** Ensure user exists before insert.

```python
# Before:
created = document_service.create_document_record(doc_payload)

# After:
document_service.ensure_user_exists(user_id, user_email)
created = document_service.create_document_record(doc_payload)
```

### Change: Add diagnostic logging to upload endpoint

```python
print(f"UPLOAD: user_id={user_id}, filename={safe_filename}, size={size}")
# After insert:
print(f"UPLOAD: document_id={doc_id}, status={created.get('status')}")
```

### Change: Add diagnostic logging to retrieval endpoint

```python
print(f"RETRIEVAL: document_id={document_id}, user_id={current_user.get('id')}")
if not doc:
    print(f"RETRIEVAL: NOT FOUND - document_id={document_id}")
if doc.get("user_id") != current_user.get("id"):
    print(f"RETRIEVAL: UNAUTHORIZED - doc.user_id={doc.get('user_id')} != current_user.id={current_user.get('id')}")
print(f"RETRIEVAL: FOUND - document_id={document_id}, filename={doc.get('filename')}")
```

### Change: Add diagnostic logging to jobs endpoint

```python
print(f"JOBS: document_id={document_id}, user_id={current_user.get('id')}")
if not doc:
    print(f"JOBS: DOCUMENT NOT FOUND - document_id={document_id}")
print(f"JOBS: FOUND {len(jobs)} jobs for document_id={document_id}")
```

---

## Verification Results

### E2E Test Results (16/16 Pass)

| # | Test | Status |
|---|------|--------|
| 1 | GET / (root) | PASS |
| 2 | Upload Markdown | PASS |
| 3 | Upload DOCX | PASS |
| 4 | GET /documents/{id} | PASS |
| 5 | GET /documents/{id}/jobs | PASS |
| 6 | POST /documents/{id}/jobs | PASS |
| 7 | POST /documents/{id}/analyze | PASS |
| 8 | POST /documents/{id}/citations/analyze | PASS |
| 9 | POST /documents/{id}/compliance/analyze | PASS |
| 10 | POST /documents/{id}/review/analyze | PASS |
| 11 | POST /documents/{id}/formatting/format | PASS |
| 12 | GET DOCX document | PASS |
| 13 | Analyze DOCX structure | PASS |
| 14 | DELETE /documents/{id} | PASS |
| 15 | DELETE /documents/{id} | PASS |
| 16 | GET /documents/ | PASS |

### Specific Validation

| Scenario | Before | After |
|----------|--------|-------|
| Upload with mock user | PASS | PASS |
| Upload with real Firebase user | FK violation → fallback UUID | User created → document persisted |
| Retrieval after upload | 404 (document not in DB) | 200 (document found) |
| Jobs after upload | 500 (document not found) | 200 (jobs returned) |
| Structure analysis | Works if document exists | Works |
| Citation analysis | Works if document exists | Works |
| Compliance analysis | Works if document exists | Works |
| Review analysis | Works if document exists | Works |
| Formatting | Works if document exists | Works |

---

## Commit

```
fix(db): ensure user exists before document insert to satisfy FK constraint

Root cause: documents.user_id has FK constraint to users.id.
Real Firebase users were never inserted into users table,
causing document insert to fail silently (fallback UUID returned).

Fix:
- Add ensure_user_exists() to create user row before document insert
- Add diagnostic logging to upload, retrieval, and jobs endpoints
- Log when fallback UUID is generated (silent failure indicator)

Verified: 16/16 E2E tests pass.
```
