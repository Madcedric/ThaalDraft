# Architecture Overview

## System Architecture

Frontend (Next.js)

↓

API Layer (FastAPI)

↓

Core Services

↓

Supabase

↓

External Research Services

---

# Frontend Layer

Responsibilities:

- Authentication
- Upload Interface
- Batch Processing UI
- Citation Workspace
- Compliance Workspace
- Reviewer Workspace

Deployment:

Vercel

---

# Backend Layer

Responsibilities:

- File Processing
- NLP Processing
- Citation Processing
- Formatting
- Compliance Validation
- Reviewer AI

Deployment:

Render

---

# Core Services

## Upload Service

Purpose:

Manage file uploads.

Supported:

- DOCX
- PDF
- TEX
- MD

Files:

services/upload/

---

## Parsing Service

Purpose:

Extract document content.

Libraries:

- PyMuPDF
- python-docx
- pylatexenc

Files:

services/parsing/

---

## NLP Service

Purpose:

Identify manuscript structure.

Libraries:

- spaCy
- SciBERT

Files:

services/nlp/

---

## Citation Service

Purpose:

Manage references and citations.

Files:

services/citations/

Submodules:

- extraction
- validation
- recommendations

---

## Formatting Service

Purpose:

Generate publication-ready outputs.

Files:

services/formatting/

Supported Formats:

- IEEE
- APA
- MLA
- ACM
- Springer
- Elsevier

---

## Compliance Service

Purpose:

Validate journal requirements.

Files:

services/compliance/

---

## Reviewer Service

Purpose:

Generate AI review feedback.

Models:

- Ollama
- Qwen
- Llama 3

Files:

services/reviewer/

---

# Database Architecture

Supabase PostgreSQL

Core Tables:

users

projects

manuscripts

processing_jobs

citations

references

compliance_reports

review_reports

exports

---

# Storage Architecture

Supabase Storage

Buckets:

raw-uploads

parsed-files

exports

reports

---

# External Services

OpenAlex

Purpose:
Reference Discovery

CrossRef

Purpose:
DOI Validation

Semantic Scholar

Purpose:
Citation Recommendations

---

# Processing Flow

Upload

↓

Storage

↓

Parsing

↓

NLP

↓

Citation Analysis

↓

Compliance Validation

↓

Formatting

↓

Reviewer AI

↓

Export

---

# Deployment Architecture

Frontend

Vercel

↓

Backend

Render

↓

Supabase

↓

External APIs

---

# Folder Structure

frontend/

backend/

docs/

services/

shared/

components/

types/

tests/
