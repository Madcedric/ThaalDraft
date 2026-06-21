# REQUIRED_CREDENTIALS.md

Before starting the V2 implementation, the following credentials and API keys must be provisioned and verified:

## 1. AI Stack
- **Gemini API Key**: Required for core reconstruction, compliance reasoning, and reviewer AI.
- **DeepSeek API Key**: Required for content generation and fallback tasks.

## 2. External Citation Sources
- **CrossRef API**: Requires registration (mailto parameter) for polite pool access.
- **OpenAlex API**: Unauthenticated by default, but requires an email for the polite pool.
- **Semantic Scholar API Key**: Required for higher rate limits during DOI resolution and citation validation.

## 3. Database & Storage (Supabase)
- **Supabase Project URL**
- **Supabase Service Role Key** (for backend operations)
- **Supabase Anon Key** (for frontend operations)
- **Database Connection String** (PostgreSQL)

## 4. Authentication (Firebase)
- **Firebase Project ID**
- **Firebase Web API Key**
- **Firebase Service Account JSON** (for backend token verification)

## 5. Deployment
- **Vercel Token/Project Link** (Frontend)
- **Render API Key/Project Link** (Backend)

*(Please provide or verify these credentials before authorizing the codebase migration).*
