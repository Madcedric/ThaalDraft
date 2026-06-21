# ThaalDraft Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                    Next.js 16 + React 19                    │
│              Tailwind CSS v4 + Shadcn UI                    │
│                   Firebase Auth SDK                         │
└──────────┬──────────────────────────────────────┬───────────┘
           │ HTTP (31 API endpoints)              │ File Upload
           ▼                                      ▼
┌─────────────────────────────────────────────────────────────┐
│                       Backend                               │
│                  FastAPI + Python 3.13                       │
│                   10 route groups                            │
├─────────────────────────────────────────────────────────────┤
│  Services Layer                                              │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │Parse   │ │Structure │ │Formatting│ │Reviewer          │ │
│  │Engine  │ │Engine    │ │Engine v2 │ │Engine v2         │ │
│  ├────────┤ ├──────────┤ ├──────────┤ ├──────────────────┤ │
│  │ Citation│ │Compliance│ │Manuscript│ │Export Engine     │ │
│  │Engine  │ │Engine    │ │Model     │ │                  │ │
│  └────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
│  ┌────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────────┐ │
│  │OCR     │ │Plagiarism│ │Ollama    │ │Submission        │ │
│  │Service │ │Service   │ │Service   │ │Builder           │ │
│  └────────┘ └──────────┘ └──────────┘ └──────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  Data Layer                                                  │
│  ┌─────────────────┐  ┌──────────────┐  ┌────────────────┐ │
│  │ Supabase        │  │ Supabase     │  │ Ollama         │ │
│  │ PostgreSQL      │  │ Storage      │  │ (local GPU)    │ │
│  └─────────────────┘  └──────────────┘  └────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

---

## Directory Structure

```
thaaldraft/
├── backend/
│   ├── app/
│   │   ├── main.py                          # FastAPI app, CORS, route registration
│   │   ├── api/routes/                      # 10 route modules
│   │   │   ├── auth.py                      # POST /login, GET /me
│   │   │   ├── health.py                    # GET /, GET /ready
│   │   │   ├── documents.py                 # CRUD + upload + parse + analyze
│   │   │   ├── exports.py                   # Export DOCX/PDF
│   │   │   ├── citations.py                 # Citation analysis
│   │   │   ├── compliance.py                # Journal compliance checks
│   │   │   ├── reviewer.py                  # AI reviewer
│   │   │   ├── formatting.py                # Formatting templates
│   │   │   ├── batch.py                     # Batch processing
│   │   │   └── submission.py                # Submission packages
│   │   ├── models/                          # Pydantic models
│   │   │   ├── document.py
│   │   │   └── user.py
│   │   └── services/
│   │       ├── manuscript/                  # Canonical manuscript model
│   │       │   ├── model.py                 # StructuredManuscript (forgiving Pydantic)
│   │       │   └── engine.py                # build_manuscript() with spaCy
│   │       ├── formatting/                  # Formatting engine
│   │       │   ├── engine_v2.py             # 6 templates (IEEE, ACM, Springer, APA, MLA, Nature)
│   │       │   ├── engine.py                # v1 (legacy)
│   │       │   ├── schema.py
│   │       │   └── templates.py
│   │       ├── reviewer/                    # AI review engine
│   │       │   ├── engine_v2.py             # Ollama-first + deterministic fallback
│   │       │   ├── analyzer.py              # v1 (legacy)
│   │       │   └── schema.py
│   │       ├── citation/                    # Citation analysis
│   │       │   ├── analyzer.py
│   │       │   ├── extractor.py
│   │       │   ├── resolver.py              # CrossRef/OpenAlex DOI resolution
│   │       │   ├── validator.py
│   │       │   ├── rules.py
│   │       │   └── schema.py
│   │       ├── compliance/                  # Journal compliance
│   │       │   ├── analyzer.py
│   │       │   ├── rules.py
│   │       │   └── schema.py
│   │       ├── structure/                   # Structure classification (v1)
│   │       │   ├── classifier.py
│   │       │   ├── metadata_extractor.py
│   │       │   ├── validator.py
│   │       │   ├── rules.py
│   │       │   └── schema.py
│   │       ├── submission/                  # Submission package builder
│   │       │   ├── builder.py
│   │       │   └── schema.py
│   │       ├── batch/
│   │       │   ├── manager.py
│   │       │   └── schema.py
│   │       ├── workers/                     # Async job workers
│   │       │   ├── parse_worker.py
│   │       │   ├── classify_worker.py
│   │       │   ├── structure_worker.py
│   │       │   ├── format_worker.py
│   │       │   ├── citation_worker.py
│   │       │   └── plagiarism_worker.py
│   │       ├── ollama_service.py            # GPU-accelerated local LLM
│   │       ├── ocr_service.py               # EasyOCR + PyMuPDF
│   │       ├── export_engine.py             # DOCX/PDF export
│   │       ├── document_service.py          # Supabase CRUD wrappers
│   │       ├── auth.py                      # Firebase JWT verification
│   │       ├── *_parser.py                  # docx/pdf/latex/markdown parsers
│   │       └── ...
│   ├── .env                                 # Secrets (not committed)
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── page.tsx                         # Landing page
│   │   ├── login/page.tsx                   # Login/signup
│   │   └── dashboard/
│   │       ├── layout.tsx                   # Sidebar + mobile navigation
│   │       ├── page.tsx                     # Workspace (upload + recent docs)
│   │       ├── documents/page.tsx           # Document list
│   │       ├── document/[id]/page.tsx       # Single document detail
│   │       ├── citations/page.tsx           # Citation overview
│   │       ├── compliance/page.tsx          # Compliance dashboard
│   │       ├── reviewer/page.tsx            # Reviewer AI dashboard
│   │       ├── formatting/page.tsx          # Formatting studio
│   │       ├── batch/page.tsx               # Batch processing
│   │       ├── submission/page.tsx          # Submission packages
│   │       └── reports/page.tsx             # Plagiarism reports
│   ├── services/api.ts                      # 31 API client functions
│   ├── types/index.ts                       # 37 TypeScript types
│   ├── hooks/                               # useAuth, useDocument, useUpload, usePlagiarism
│   ├── components/                          # Shadcn UI + custom components
│   └── lib/                                 # Auth context, Firebase init, utilities
```

---

## API Endpoints (31 total)

All routes are prefixed under `/api/v1` and protected by Firebase JWT auth.

| Module       | Method | Endpoint                                | Purpose                         |
|--------------|--------|----------------------------------------|----------------------------------|
| **Auth**     | POST   | `/auth/login`                          | Dev login (mock token)          |
|              | GET    | `/auth/me`                             | Current user profile            |
| **Health**   | GET    | `/health/`                             | Liveness check                  |
|              | GET    | `/health/ready`                        | Readiness check                 |
| **Documents**| POST   | `/documents/upload`                    | Upload + parse + store          |
|              | POST   | `/documents/parse`                     | Parse only (no persistence)     |
|              | GET    | `/documents/`                          | List user documents             |
|              | GET    | `/documents/{id}`                      | Get single document             |
|              | PATCH  | `/documents/{id}`                      | Update metadata                 |
|              | DELETE | `/documents/{id}`                      | Delete document                 |
|              | POST   | `/documents/{id}/analyze`              | Structure analysis              |
|              | GET    | `/documents/{id}/structure`            | Get structured data             |
|              | POST   | `/documents/{id}/jobs`                 | Enqueue job                     |
|              | GET    | `/documents/{id}/jobs`                 | List jobs                       |
|              | POST   | `/documents/format`                    | Format uploaded file            |
|              | POST   | `/documents/{id}/plagiarism/analyze`   | Run plagiarism check            |
|              | GET    | `/documents/{id}/plagiarism`           | Get plagiarism report           |
| **Exports**  | POST   | `/documents/{id}/export`               | Export DOCX/PDF                 |
|              | GET    | `/documents/{id}/exports`              | List exports                    |
|              | GET    | `/documents/download/{export_id}`      | Download export file            |
| **Citations**| POST   | `/documents/{id}/citations/analyze`    | Analyze citations               |
|              | GET    | `/documents/{id}/citations`            | Get citation report             |
|              | GET    | `/documents/{id}/citations/health`     | Get citation health score       |
| **Compliance**| GET   | `/documents/compliance/journals`       | List supported journals         |
|              | GET    | `/documents/compliance/journals/{id}`  | Get journal rules               |
|              | POST   | `/documents/{id}/compliance/analyze`   | Check compliance                |
|              | GET    | `/documents/{id}/compliance`           | Get compliance report           |
| **Reviewer** | POST   | `/documents/{id}/review/analyze`       | Run AI review                   |
|              | GET    | `/documents/{id}/review`               | Get review report               |
| **Formatting**| GET   | `/formatting/templates`                | List templates                  |
|              | GET    | `/formatting/templates/{id}`           | Get template details            |
|              | POST   | `/documents/{id}/formatting/preview`   | Validate formatting             |
|              | POST   | `/documents/{id}/formatting/format`    | Apply format template           |
|              | GET    | `/documents/{id}/formatting`           | Get formatting status           |
| **Batch**    | POST   | `/batch/create`                        | Create batch job                |
|              | POST   | `/batch/{id}/files`                    | Add files to batch              |
|              | POST   | `/batch/{id}/start`                    | Start batch                     |
|              | GET    | `/batch/{id}/status`                   | Batch status                    |
|              | POST   | `/batch/{id}/cancel`                   | Cancel batch                    |
|              | GET    | `/batch/jobs`                          | List batch jobs                 |
|              | DELETE | `/batch/{id}`                          | Delete batch                    |
| **Submission**| POST  | `/documents/{id}/submission/build`     | Build submission package        |
|              | GET    | `/documents/{id}/submission`           | Get package                     |
|              | GET    | `/documents/{id}/submission/download-zip` | Download ZIP               |
|              | GET    | `/submission/packages`                 | List packages                   |

---

## Data Models

### Backend: StructuredManuscript (Canonical Model)

```
StructuredManuscript
├── id: str (UUID, auto-generated if missing)
├── title: str
├── authors: list[Author]
│   └── Author: { name, affiliation?, email?, orcid? }
├── abstract: str
├── keywords: list[str]
├── sections: list[ManuscriptSection]
│   └── ManuscriptSection:
│       ├── heading: str
│       ├── label: SectionType (enum: abstract|introduction|related_work|
│       │         methodology|methods|experiments|results|discussion|
│       │         conclusion|conclusions|references|acknowledgments|
│       │         appendix|keywords|figure|table|other)
│       ├── content: str
│       ├── level: int
│       ├── confidence: float (0-1)
│       ├── tables: list[Table]
│       └── figures: list[Figure]
├── references: list[Reference]
│   └── Reference: { index, authors, title, year, doi, journal, raw_text }
├── tables: list[Table]
├── figures: list[Figure]
├── word_count: int
├── section_count: int
├── reference_count: int
└── metadata: dict
```

### Frontend: Document

```
Document
├── id: string
├── filename: string
├── status: DocumentStatus (uploaded|parsing|parsed|...|structured|formatted|failed)
├── parsed_json: StructuredData?
│   ├── title, authors, abstract, keywords, sections, references
│   ├── citation_report?: CitationReport
│   ├── compliance_report?: ComplianceReport
│   ├── review_report?: ReviewReport
│   └── manuscript_model?: dict (serialized StructuredManuscript)
├── file_type, size_bytes, created_at, updated_at
└── selected_journal?: string
```

---

## Service Architecture

### Processing Pipeline (v2 — Manuscript-Centric)

```
Upload File
    │
    ▼
┌──────────────────┐
│  Document Parser  │  .docx → python-docx
│  (per extension)  │  .pdf  → PyMuPDF (+ OCR fallback)
└──────┬───────────┘  .tex  → regex
       │              .md   → regex
       ▼
┌──────────────────┐
│  Structure Engine │  spaCy NER (authors)
│  build_manuscript │  Section classification (heading + content + position)
└──────┬───────────┘  Table/figure detection
       │              Reference parsing (DOI, year, title)
       ▼
┌──────────────────┐
│ StructuredManuscript│  Canonical model stored in parsed_json
│  (forgiving model)  │  Missing fields → defaults (UUID, 0, [])
└──────┬───────────┘
       │
       ├──→ Formatting Engine v2
       │       └── 6 templates: IEEE, ACM, Springer, APA, MLA, Nature
       │       └── validate_manuscript() scoring
       │
       ├──→ AI Reviewer v2
       │       └── Ollama (qwen3:4b on GPU, 300s timeout)
       │       └── Deterministic fallback (0ms, rule-based)
       │
       ├──→ Citation Analyzer
       │       └── DOI resolution via CrossRef/OpenAlex (off by default)
       │       └── Citation health scoring
       │
       ├──→ Compliance Analyzer
       │       └── Journal-specific rules (8 journals)
       │       └── Word count, structure, reference rules
       │
       ├──→ Plagiarism Checker
       │       └── SentenceTransformer embeddings + Jaccard
       │       └── Cross-document similarity
       │
       └──→ Export Engine
               └── DOCX generation (python-docx)
               └── PDF conversion (docx2pdf / LibreOffice)
```

### AI Priority (per guidelines)
1. **Deterministic logic** (rules, regex, heuristics)
2. **NLP models** (spaCy NER, SentenceTransformer embeddings)
3. **Embeddings** (semantic similarity for section classification)
4. **LLM** (Ollama review — only when deterministic insufficient)

---

## Database

**Supabase PostgreSQL** with 5 tables:

| Table              | Key Fields                                    | Purpose                         |
|--------------------|-----------------------------------------------|----------------------------------|
| `users`            | `id`, `email`, `name`, `provider`             | User accounts                   |
| `documents`        | `id`, `user_id`, `filename`, `status`,        | Uploaded documents +            |
|                    | `parsed_json` (JSONB), `file_type`,           | all analysis results            |
|                    | `size_bytes`, `created_at`                    |                                  |
| `jobs`             | `id`, `document_id`, `type`, `status`,        | Async job queue                 |
|                    | `payload`, `result`, `created_at`             |                                  |
| `exports`          | `id`, `document_id`, `format`, `storage_path`, | Generated export files          |
|                    | `created_at`                                  |                                  |
| `plagiarism_checks`| `id`, `document_id`, `similarity_score`,      | Plagiarism results              |
|                    | `report` (JSONB), `created_at`                |                                  |

All database access is via direct HTTP to Supabase REST API — no ORM.

---

## Security

| Layer            | Mechanism                                         |
|------------------|---------------------------------------------------|
| Authentication   | Firebase JWT (RS256), verified via X.509 certs    |
| API Protection   | `Depends(get_current_user)` on every route         |
| Dev fallback     | Mock user when Firebase is unconfigured            |
| Database         | Supabase service role key (bypasses RLS)           |
| Secrets          | `.env` file, gitignored                           |
| CORS             | Restricted to localhost:3000 + vercel.app domains |

---

## Key Design Decisions

| Decision | Rationale |
|----------|-----------|
| **Forgiving StructuredManuscript** | Old documents lack `id`, `index`, `authors`; defaults prevent 169 validation errors |
| **Upload = parse + store only** | Heavy analysis (citations, review, compliance) runs on-demand; upload is ~2s vs 30-120s |
| **DOI resolution off by default** | 20-60s blocking time; let users opt-in with `resolve_dois=True` |
| **Ollama-first + deterministic fallback** | LLM quality when available (GPU); 0ms fallback ensures no review failure |
| **spaCy preloaded at boot** | Cold start is 15s; paid once at deployment, not on every request |
| **No ORM** | Direct Supabase REST keeps dependencies minimal; SQL knowledge sufficient |
| **V1 + V2 engines coexist** | Routes migrated to v2 incrementally; v1 preserved for backward compatibility |
| **In-memory batch/submission stores** | Simple, fast; no persistence across restarts (acceptable for SaaS with Supabase) |
| **LRU-cached spaCy/SentenceTransformer** | Models loaded once, reused across requests |
