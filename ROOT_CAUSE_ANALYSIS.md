# ROOT_CAUSE_ANALYSIS.md — "Document Not Found"

## Symptom
After a document upload completes successfully and the user is redirected to the document view, the frontend eventually shows: "Something went wrong" or "Document not found". Subsequent API calls return 404/500 errors.

## Trace & Root Cause
The root cause lies in `backend/app/services/document_service.py` within the `create_document_record` function, combined with a Foreign Key constraint failure.

1. **Upload Request**: The frontend sends the file to `POST /upload` with the user's Firebase token.
2. **Database Insert Failure**: The backend attempts to insert a record into the Supabase `documents` table. However, because the user's Firebase UID is not yet synchronized or present in the Supabase `users` table, a Foreign Key constraint (`user_id` references `users(id)`) fails, blocking the insert.
3. **Silent Fallback**: In `create_document_record`, there is a catch block that masks this failure. Instead of returning an error, it generates a random UUID (`fallback_id = str(uuid.uuid4())`), attaches it to the payload, and returns 200 OK to the frontend.
4. **Data Loss**: The file is stored in Supabase Storage, but no database row is created.
5. **Frontend Failure**: The frontend receives the random UUID, navigates to `/dashboard/document/{fallback-id}`, and makes a `GET` request. Because the row was never actually created, the backend returns a 404.

## Conclusion
The application is masking critical database failures with a silent fallback UUID mechanism, leading to a disconnected upload flow.

## Fix Strategy (Deferred)
To fix this, we must ensure the `users` table is always populated prior to the `documents` insert (e.g., via an `ensure_user_exists` upsert check), and we must remove the fake UUID generation fallback so that database errors correctly fail the upload request and prompt a retry.
