# ThaalDraft — Process Flow

## User Journey Overview

```
              ┌──────────┐
              │  Upload  │
              │ Document │
              └────┬─────┘
                   │
                   ▼
              ┌──────────┐
              │  Parse & │
              │  Store   │
              └────┬─────┘
                   │
     ┌─────────────┼─────────────┬──────────────┐
     ▼             ▼             ▼              ▼
┌──────────┐ ┌──────────┐ ┌──────────┐  ┌──────────┐
│Structure │ │Citation  │ │Compliance│  │Reviewer  │
│Analysis  │ │Analysis  │ │Check     │  │AI        │
└────┬─────┘ └────┬─────┘ └────┬─────┘  └────┬─────┘
     │            │            │              │
     └────────────┼────────────┼──────────────┘
                  ▼            ▼
             ┌──────────┐ ┌──────────┐
             │ Format   │ │ Export   │
             │ (6 temp.)│ │ DOCX/PDF│
             └────┬─────┘ └────┬─────┘
                  │            │
                  ▼            ▼
             ┌──────────────────────┐
             │  Submission Package  │
             │  (ZIP with all docs) │
             └──────────────────────┘
```

---

## 1. Document Upload & Parsing

```
User Action:
  [Dashboard] → Click "Upload" / Drag file to drop zone
       │
       ▼
Frontend (workspace page):
  POST /api/v1/documents/upload  (FormData: file)
  File types: .docx, .pdf, .tex, .md
  Max size: 50 MB
       │
       ▼
Backend (documents.py — upload_document):
  1. validate_file() — extension + size check
  2. save_upload_file() — save to local uploads/
  3. parse_document() → dispatches to:
       .docx → docx_parser.py  (python-docx)
       .pdf  → pdf_parser.py   (PyMuPDF)
               or ocr_service   (EasyOCR fallback if <100 chars)
       .tex  → latex_parser.py (regex)
       .md   → markdown_parser.py (regex)
  4. build_manuscript() → spaCy NER (authors)
       → Section classification (heading + content + position)
       → Table/figure detection
       → Reference parsing
  5. create_document_record() → Supabase
       Status = "structured"
  6. Return DocumentMeta { id, filename, status }
       │
       ▼
Frontend:
  Navigate to /dashboard/document/{id}
```

### Duration
| File Type | Parse Time |
|-----------|-----------|
| .md       | <50 ms    |
| .docx     | 100-300 ms|
| .tex      | 50-100 ms |
| .pdf (text) | 200-500 ms |
| .pdf (scanned) | 5-30s (OCR) |

---

## 2. Document Detail Page

```
Frontend (/dashboard/document/[id]):
  GET /api/v1/documents/{id}
       │
       ▼
  Header: Title, ID, Status badge
  Metrics: File Type, File Size, Word Count, References
  Info: Filename, Created date, Authors, Confidence badge
  Actions:
    ┌──────────────────────────────────────────┐
    │  Structure Analysis  │  Citation Analysis │
    │  Compliance Check    │  Reviewer AI       │
    │  Format Document     │  Plagiarism Check  │
    └──────────────────────────────────────────┘
  Export: [DOCX] [PDF]
  Sections: Section summary with confidence scores
  Abstract
  Processing history (jobs list)
```

---

## 3. Structure Analysis

```
User clicks "Structure Analysis"
       │
       ▼
Frontend:
  POST /api/v1/documents/{id}/analyze
       │
       ▼
Backend (documents.py — analyze_document_structure):
  1. Get document from Supabase
  2. If parsed_json has no sections → return as-is
  3. Build StructuredManuscript via build_manuscript()
  4. Update parsed_json.manuscript_model in Supabase
  5. Return { document_id, structured, status }
       │
       ▼
Backend (internal — structure engine):
  Section classification:
    ┌─────────────────────────────────────────────┐
    │  1. Heading exact match (95% confidence)     │
    │     "Introduction" → SectionType.INTRODUCTION │
    │  2. Keyword partial match (80% confidence)   │
    │     "Related Work Survey" → RELATED_WORK     │
    │  3. Content signal analysis (50-70%)         │
    │     "we propose, our method" → METHODOLOGY   │
    │  4. Position heuristic (position in doc)     │
    │     First section → likely INTRODUCTION      │
    └─────────────────────────────────────────────┘
  Author extraction: spaCy PERSON NER on title text
  Reference parsing: DOI regex, year detection, title extraction
       │
       ▼
Frontend:
  Updates sections summary + confidence display
  Shows detected section types
```

### Output
- 9+ section types detected (abstract, introduction, related_work, methodology, methods, experiments, results, discussion, conclusion, references, acknowledgments, appendix)
- Authors extracted via NER
- Tables/figures detected from content markers
- References parsed (DOI, year, title)

---

## 4. Citation Analysis

```
User clicks "Citation Analysis"
       │
       ▼
Frontend:
  POST /api/v1/documents/{id}/citations/analyze
       │
       ▼
Backend (citations/analyzer.py — analyze_citations):
  1. Load StructuredManuscript from parsed_json
  2. Extract citation markers from section content
     (numbered [1], author-year "Smith et al., 2020")
  3. Detect citation style (IEEE, ACM, APA, MLA, etc.)
  4. Validate each citation against references list
  5. Optionally resolve DOIs via CrossRef/OpenAlex
     (default: resolve_dois=false, max 10 refs, 5s timeout)
  6. Calculate citation health score:
     - Reference coverage
     - Citation validity
     - Duplicate score
     - DOI completeness
  7. Store citation_report in parsed_json
  8. Return { report, status }
       │
       ▼
Frontend:
  Shows citation health score, resolved/unresolved counts,
  citation issues, reference validation
```

### Scoring
| Component | Weight |
|-----------|--------|
| Reference coverage | % of references cited in text |
| Citation validity | % of citations matching valid references |
| Duplicate check | How many references cited multiple times |
| DOI coverage | % of references with valid DOIs |

---

## 5. Compliance Check

```
User clicks "Compliance Check"
  → Select target journal from picker
       │
       ▼
Frontend:
  GET /api/v1/documents/compliance/journals  (list journals)
  POST /api/v1/documents/{id}/compliance/analyze
       Body: { journal_id: "ieee" }
       │
       ▼
Backend (compliance/analyzer.py — analyze_compliance):
  1. Load journal rules for selected journal
  2. Check each rule against StructuredManuscript:
     ┌────────────────────────────────────────────┐
     │  Rule                   │ What's checked    │
     ├─────────────────────────┼───────────────────┤
     │ Word count              │ min/max words     │
     │ Abstract length         │ min/max words     │
     │ Reference count         │ min/max refs      │
     │ Citation style          │ matches journal   │
     │ Figure limit            │ max figures       │
     │ Section structure       │ required sections │
     │ Keyword count           │ min/max keywords  │
     │ Title length            │ max words         │
     │ DOI requirement         │ DOI needed?      │
     └────────────────────────────────────────────┘
  3. Calculate compliance score (0-100)
  4. Store compliance_report in parsed_json
  5. Return { report, status }
       │
       ▼
Frontend:
  Shows pass/fail/warn per rule
  Overall compliance score
  Recommendations for failed checks
```

### Supported Journals
IEEE, ACM, Springer, Elsevier, APA, MLA, Nature, Custom

---

## 6. AI Reviewer

```
User clicks "Reviewer AI"
       │
       ▼
Frontend:
  POST /api/v1/documents/{id}/review/analyze
       │
       ▼
Backend (reviewer/engine_v2.py — review_manuscript):
  1. Check Ollama availability
  2. Convert StructuredManuscript to text (max 8000 chars)
       │
       ├── [Ollama Available] ──────────────────────────┐
       │  Call ollama with structured review prompt      │
       │  Model: qwen3:4b (GPU-accelerated)              │
       │  Timeout: 300s                                  │
       │  ┌─────────────────────────────────────────┐    │
       │  │ Prompt: Review the manuscript, return    │    │
       │  │ JSON with strengths, weaknesses,         │    │
       │  │ category_scores (6 categories),          │    │
       │  │ publication_readiness                    │    │
       │  └─────────────────────────────────────────┘    │
       │  │                                              │
       │  ├── [Success] → Parse JSON response            │
       │  │   analysis_method = "llm (ollama)"           │
       │  │                                              │
       │  └── [Timeout/Fail] → Fallback to deterministic │
       │                                                │
       └── [Ollama Unavailable] ────────────────────────┘
          │
          ▼
  3. deterministic_review() — rule-based:
     ┌──────────────────────────────────┐
     │ Category             │ Method    │
     ├──────────────────────┼───────────┤
     │ Writing quality      │ Word count, section balance │
     │ Research clarity     │ Missing required sections   │
     │ Methodology          │ Has methods/experiments?    │
     │ Literature coverage  │ Reference count             │
     │ Citation completeness│ Has any references?         │
     │ Research gaps        │ Future work / limitations   │
     └──────────────────────────────────┘
  4. Calculate overall score → label
     ≥85: Ready | ≥70: Conditionally Ready
     ≥50: Needs Revision | <50: Not Ready
  5. Store review_report in parsed_json
       │
       ▼
Frontend:
  Shows overall score + readiness label
  Per-category scores (6 areas)
  Strengths list
  Weaknesses list (with severity: critical/major/minor/suggestion)
  Improvement suggestions
  Analysis method badge: "LLM (Ollama)" or "Deterministic"
```

### Review Categories
| Category | What It Measures |
|----------|-----------------|
| writing_quality | Grammar, clarity, section balance |
| research_clarity | Structure completeness (intro, methods, results, conclusion) |
| methodology | Presence of methods/experiments section |
| literature_coverage | Adequate reference count |
| citation_completeness | References linked to citations |
| research_gaps | Future work, limitations discussed |

---

## 7. Formatting

```
User clicks "Format Document"
  → Select template from grid
       │
       ▼
Frontend:
  GET /api/v1/formatting/templates  (list 6 templates)
  POST /api/v1/documents/{id}/formatting/format
       Body: { template_id: "ieee" }
       │
       ▼
Backend (formatting/engine_v2.py — format_manuscript):
  1. Load StructuredManuscript from parsed_json
  2. Load FormatConfig for selected template
  3. Validate manuscript against template requirements
  4. Generate DOCX:
     ┌──────────────────────────────────────────────┐
     │  Template   │ Section Style  │ Reference     │
     ├─────────────┼────────────────┼───────────────┤
     │ IEEE        │ Roman numerals │ [1], [2]      │
     │ ACM         │ Numbered       │ [1], [2]      │
     │ Springer    │ Numbered       │ [1], [2]      │
     │ APA         │ Named sections │ (Author, year)│
     │ MLA         │ Named sections │ (Author page) │
     │ Nature      │ Numbered       │ superscript    │
     └──────────────────────────────────────────────┘
  5. Apply margins, fonts, heading styles
  6. Format references per template style
  7. Add tables (Table Grid style)
  8. Return { output, validation, status }
       │
       ▼
Frontend:
  Enable download button
```

### Format Validation Score
| Component | Max Score |
|-----------|-----------|
| Title present | 10 |
| Abstract present | 10 |
| Sections non-empty | 20 |
| Required sections met | 20 |
| Reference count ≥ 5 | 15 |
| Min word count met | 15 |
| Authors present | 10 |

---

## 8. Export

```
User clicks "Export DOCX" or "Export PDF"
       │
       ▼
Frontend:
  POST /api/v1/documents/{id}/export
       Body: { template: "ieee", format: "docx" }
       │
       ▼
Backend (exports.py — request_export / export_engine.py):
  1. Load StructuredManuscript from parsed_json
  2. Format via engine_v2.format_manuscript()
  3. If PDF: convert DOCX → PDF (docx2pdf / LibreOffice)
  4. Return file as response
     (Content-Disposition with server-generated filename)
       │
       ▼
Frontend:
  Download file with correct extension and content-type
```

---

## 9. Submission Package

```
User clicks "Build Package"
       │
       ▼
Frontend:
  POST /api/v1/documents/{id}/submission/build
       Body: { journal_id, template_id, components?: [...] }
       │
       ▼
Backend (submission/builder.py — build_submission_package):
  1. Generate requested components:
     ┌────────────────────────────────┐
     │ Component         │ Source     │
     ├────────────────────┼───────────┤
     │ Manuscript DOCX    │ formatting│
     │ Manuscript PDF     │ export    │
     │ Compliance Report  │ compliance│
     │ Review Report      │ reviewer  │
     │ Citation Report    │ citations │
     │ Cover Letter       │ generated │
     │ Author Statement   │ generated │
     │ Conflict Statement │ generated │
     └────────────────────────────────┘
  2. Package into ZIP archive
  3. Store at submission_packages/
  4. Return { package, total_components, completed, failed, progress }
       │
       ▼
Frontend:
  Shows component status per document
  Enable ZIP download button
```

---

## 10. Plagiarism Check

```
User clicks "Plagiarism Check"
       │
       ▼
Frontend:
  POST /api/v1/documents/{id}/plagiarism/analyze
       │
       ▼
Backend (documents.py — analyze_plagiarism):
  1. Build text from document sections
  2. Fetch other user documents as corpus
  3. compute_similarity(target, each_other_doc):
     ┌────────────────────────────────┐
     │  1. SentenceTransformer        │
     │     all-MiniLM-L6-v2 embeddings │
     │  2. Cosine similarity           │
     │  3. Fallback: 5-gram Jaccard   │
     │     (if embeddings fail)       │
     └────────────────────────────────┘
  4. Return top-N matches with scores
  5. Store plagiarism_checks record
       │
       ▼
Frontend (reports page):
  Shows similarity score, matched sources
```

---

## System Interaction Diagram

```
┌─────────┐     ┌──────────┐     ┌───────────┐     ┌──────────┐
│ Frontend │────▶│ Routes   │────▶│ Services  │────▶│ App/Data │
└─────────┘     └──────────┘     └───────────┘     └──────────┘
     │               │                │                │
     │ HTTP/JSON     │ FastAPI        │ Python          │ Supabase
     │ Auth: Bearer  │ 10 routers     │ Modular         │ REST API
     │ File upload   │ Depends(auth)  │ LRU-cached NLP  │ Storage
                                                                
     External:                    External:
     Firebase Auth                CrossRef/OpenAlex (DOI)
                                  Ollama (GPU LLM)
```

---

## Data Lifecycle

```
Upload ──→ Parse ──→ Structure ──→ Analyze ──→ Format ──→ Export ──→ Submit
  │          │           │            │            │          │          │
  ▼          ▼           ▼            ▼            ▼          ▼          ▼
Local    parsed_json  manuscript_  citation/    formatted   .docx     .zip
file     (JSONB)      model        compliance/  file        .pdf
                                    review
                                    reports
                        ┌──────────────────────────────────────────┐
                        │  All analysis reports stored inside      │
                        │  parsed_json (JSONB column in Supabase)  │
                        └──────────────────────────────────────────┘
```

## Status Flow

```
uploaded → parsing → parsed → classifying → classified
  → structuring → structured → formatting → formatted → exported
                                    │
                                    └→ failed (any step)
```

Upload sets status to `"structured"` (heavy analysis removed from upload step; runs on-demand).
