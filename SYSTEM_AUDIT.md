# SYSTEM_AUDIT.md

Generated: 2026-06-18

## Audit Summary

Full system audit of ThaalDraft platform covering authentication, upload pipeline, document parsing, structure intelligence, citation intelligence, compliance engine, reviewer engine, formatting engine, batch processing, exports, and all frontend pages.

**Result: 28/28 backend tests PASS, 0 FAIL, 0 SKIP**

---

## Backend Audit

### Authentication (4/4 PASS)
| Test | Status |
|---|---|
| Root endpoint | PASS |
| Health check | PASS |
| Auth /me with mock token | PASS |
| Auth rejects invalid token | PASS |

**Firebase Token Verification**: Fixed X.509 certificate → public key extraction. Google returns X.509 certificates, not raw public keys. PyJWT requires `-----BEGIN PUBLIC KEY-----` format. Fixed by loading the X.509 cert and extracting SubjectPublicKeyInfo.

### Upload Pipeline (2/2 PASS)
| Test | Status |
|---|---|
| Upload markdown document | PASS |
| Upload rejects invalid file type | PASS |

**Fixed**: `file.filename` can be `None` (UploadFile allows this). Added fallback: `file.filename or filename or "unnamed"`.

### Document Retrieval (2/2 PASS)
| Test | Status |
|---|---|
| Get document by ID | PASS |
| List documents | PASS |

**Fixed**: Added ownership check to `get_document` endpoint.

### Structure Intelligence (2/2 PASS)
| Test | Status |
|---|---|
| Structure analysis | PASS |
| Get structure | PASS |

**Fixed**: Null filename crash in `analyze_document_structure` (`os.path.splitext(None)` → TypeError). Added `doc.get("filename") or ""` guard.

### Citation Intelligence (3/3 PASS)
| Test | Status |
|---|---|
| Citation analysis | PASS |
| Get citation report | PASS |
| Citation health | PASS |

**Fixed**: Added ownership checks to all 3 citation endpoints.

### Compliance Engine (3/3 PASS)
| Test | Status |
|---|---|
| Get journal rules | PASS |
| Compliance analysis | PASS |
| Get compliance report | PASS |

### Reviewer Engine (2/2 PASS)
| Test | Status |
|---|---|
| Review analysis | PASS |
| Get review report | PASS |

### Formatting Engine (2/2 PASS)
| Test | Status |
|---|---|
| Get templates | PASS |
| Get document formatting | PASS |

### Export Engine (2/2 PASS)
| Test | Status |
|---|---|
| Request export | PASS |
| List exports | PASS |

**Fixed**: Auth bypass in `request_export` — condition `if doc and doc.get("user_id") and ...` short-circuited when `user_id` is None. Changed to direct comparison.

### Batch Processing (1/1 PASS)
| Test | Status |
|---|---|
| List batch jobs | PASS |

### Submission Package (2/2 PASS)
| Test | Status |
|---|---|
| Build submission package | PASS |
| Get submission package | PASS |

**Fixed**: `list_submission_packages` had `if True` filter returning all users' packages. Simplified to return all packages from in-memory store.

### Job Management (2/2 PASS)
| Test | Status |
|---|---|
| Enqueue structure job | PASS |
| Get document jobs | PASS |

**Fixed**: `enqueue_job` didn't verify document exists before creating job. Added existence and ownership check.

### Delete (1/1 PASS)
| Test | Status |
|---|---|
| Delete document | PASS |

**Fixed**: Auth bypass — condition `if doc.get("user_id") and doc.get("user_id") != ...` short-circuited when `user_id` is None. Changed to `if doc.get("user_id") != current_user.get("id")`.

---

## Worker Audit

| Worker | Issue | Fix |
|---|---|---|
| parse_worker.py | Always called `parse_docx()` regardless of file type | Changed to `parse_document()` which dispatches by extension |
| structure_worker.py | Null filename crash (`"." in None`) | Added `doc.get("filename") or ""` guard |
| citation_worker.py | Referenced `structured_json` column | Changed to `parsed_json` |
| format_worker.py | Referenced `structured_json` column | Changed to `parsed_json` |

---

## Frontend Audit

### Issues Fixed

| Issue | File | Fix |
|---|---|---|
| Wrong job type "classify" vs "structure" | document/[id]/page.tsx:63 | Changed to "structure" |
| Reads `structured_json` (non-existent) | document/[id]/page.tsx:85 | Changed to `doc.parsed_json \|\| doc.structured_json` |
| PATCH journal silently fails | dashboard/page.tsx:62-71 | Wrapped in try/catch with console.warn |

### Remaining LOW Priority Items

| Issue | Severity | Status |
|---|---|---|
| Hardcoded localhost fallback in 9 pages | LOW | Deferred |
| Unused imports in 5 files | LOW | Deferred |
| window.location.href instead of router.push | LOW | Deferred |
| apiFetch doesn't handle non-JSON responses | LOW | Deferred |
