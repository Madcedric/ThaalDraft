# Database migrations

Migrations for Supabase / Postgres are stored here under `backend/db/migrations/`.

To apply them locally, you can use the `psql` client or Supabase CLI. Example using `psql`:

```bash
# Export connection string
export DATABASE_URL=postgres://user:pass@host:5432/dbname

# Run each migration in order
psql "$DATABASE_URL" -f backend/db/migrations/01_extensions.sql
psql "$DATABASE_URL" -f backend/db/migrations/02_users.sql
psql "$DATABASE_URL" -f backend/db/migrations/03_documents.sql
psql "$DATABASE_URL" -f backend/db/migrations/04_jobs.sql
psql "$DATABASE_URL" -f backend/db/migrations/05_plagiarism_exports.sql
psql "$DATABASE_URL" -f backend/db/migrations/06_indexes.sql
psql "$DATABASE_URL" -f backend/db/migrations/07_rls_policies.sql
```

Or use the Supabase SQL editor to paste and run each file.
