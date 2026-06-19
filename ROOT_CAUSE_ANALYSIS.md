# ROOT_CAUSE_ANALYSIS.md — Document Not Found After Upload

**Date:** June 19, 2026
**Severity:** Critical
**Status:** Fixed and verified

---

## Symptom

1. File uploads successfully (200 response with valid UUID)
2. Frontend redirects to `/dashboard/document/{uuid}`
3. Document page shows: "Something went wrong - Document not found"
4. Console: `GET /api/v1/documents/{uuid}/jobs` → 500 Internal Server Error
5. Backend returns: 404 Document not found

---

## Root Cause: Foreign Key Constraint on `user_id`

### Schema

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id TEXT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    ...
);
```

The `documents` table has a **foreign key constraint**: `user_id` must exist in the `users` table.

### The Failure Chain

1. User signs in with Google → Firebase assigns real UID (e.g., `abc123xyz456`)
2. Frontend sends Firebase token to `POST /api/v1/documents/upload`
3. Auth module verifies token → returns `{"id": "abc123xyz456", "email": "user@gmail.com"}`
4. Upload creates document payload with `user_id = "abc123xyz456"`
5. **Supabase insert fails** with FK violation (user `abc123xyz456` doesn't exist in `users` table)
6. `create_document_record()` catches the error, generates **fallback UUID**
7. Returns fallback UUID to frontend (not persisted in database)
8. Frontend navigates to `/dashboard/document/{fallback-uuid}`
9. `get_document()` queries Supabase → **document doesn't exist** → returns `None`
10. Backend returns 404 → frontend shows "Document not found"

### Why Mock Users Worked

During testing, the auth module returned `mock-user-123` (because tokens started with `mock-` or `FIREBASE_PROJECT_ID` was not configured). The `mock-user-123` user **does exist** in the `users` table, so FK constraint was satisfied.

### Why Real Users Failed

When a real user signs in with Google:
- Auth module extracts real Firebase UID from token
- This UID is NOT in the `users` table
- FK constraint blocks document insert
- Fallback UUID is returned (not persisted)

### Diagnostic Evidence

```
TEST 8: RLS CHECK — Insert with fake user_id
  Insert status: 409
  Response: {"code":"23503","message":"insert or update on table \"documents\"
    violates foreign key constraint \"documents_user_id_fkey\"",
    "details":"Key (user_id)=(nonexistent-user-xyz) is not present in table \"users\"."}
  CONFIRMED: FK constraint is blocking inserts!
```

---

## Fix Applied

### `document_service.py` — `ensure_user_exists()`

New function that creates the user row in `users` table before document insert:

```python
def ensure_user_exists(user_id: str, email: str = "") -> bool:
    """Ensure a user row exists in Supabase. Creates it if missing (idempotent)."""
    # Check if user exists
    r = requests.get(f"{url}?id=eq.{user_id}&select=id", ...)
    if r.json():
        return True  # User exists

    # Insert user (upsert to avoid duplicate errors)
    r = requests.post(url, json=[{"id": user_id, "email": email, "provider": "firebase"}], ...)
    return r.status_code in (200, 201)
```

### `documents.py` — Upload endpoint calls `ensure_user_exists()`

```python
# Before insert:
document_service.ensure_user_exists(user_id, user_email)
created = document_service.create_document_record(doc_payload)
```

---

## Verification

| Test | Before Fix | After Fix |
|------|-----------|-----------|
| Upload with mock user | PASS | PASS |
| Upload with real Firebase user | FK violation → fallback UUID | User created → document persisted |
| Retrieval after upload | 404 (document not in DB) | 200 (document found) |
| Jobs after upload | 500 (document not found) | 200 (jobs returned) |
| Full pipeline (16 tests) | Intermittent failures | 16/16 pass |

---

## Key Insight

The `create_document_record()` fallback mechanism (generating UUID when insert fails) **masks the real error**. The function returns a valid-looking UUID, but the row was never created. This is a silent failure that only manifests when the client tries to retrieve the document.

**Lesson:** Always verify that database operations actually persist data. A 201 response from Supabase means the row was created, but a fallback UUID means the row was NOT created.
