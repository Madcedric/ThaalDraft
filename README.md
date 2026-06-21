# ThaalDraft

### AI-Powered Manuscript Reconstruction & Journal Formatting Platform

ThaalDraft transforms raw research documents into publication-ready manuscripts.

Instead of only changing fonts and layouts, ThaalDraft reconstructs document structure, validates citations, performs compliance checks, reviews manuscript quality, and formats papers into journal-specific templates.

---

## 🔐 Authentication Architecture

The system uses **Firebase Authentication** for user registration, sessions, and social login (Google OAuth).

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Frontend as Next.js Web App
    participant Firebase as Firebase Auth
    participant Backend as FastAPI Server

    User->>Frontend: Enter Credentials / Click Google Sign-In
    Frontend->>Firebase: Authenticate User
    Firebase-->>Frontend: Return ID Token (JWT)
    Frontend->>Backend: API Request + Authorization: Bearer <ID_TOKEN>
    Backend->>Backend: Verify Signature (using Google's Public Keys)
    Backend->>Backend: Validate Claims (Audience, Expiry)
    Backend-->>Frontend: Return Processed Data / Formatted File
    Frontend-->>User: Download File / Show Dashboard
```

## Problem

Researchers frequently work with:

- Unstructured DOCX drafts
- Poorly formatted PDFs
- Missing citations and DOI metadata
- Journal-specific formatting requirements

Manual formatting is time-consuming and error-prone.

ThaalDraft automates the entire workflow.

---

## Core Features

### Reconstruction Mode

Convert raw documents into structured manuscripts.

- DOCX ZIP/XML extraction
- PDF text extraction
- Figure and table detection
- Section reconstruction
- Canonical manuscript generation

### Formatting Studio

Supported formats:

- IEEE
- Elsevier
- Custom Templates

Upcoming:

- Springer
- ACM
- Nature
- APA
- MLA

### Reviewer AI

AI-assisted manuscript evaluation:

- Writing quality analysis
- Research quality assessment
- Missing section detection
- Publication readiness review

### DOI Intelligence

Powered by:

- CrossRef
- OpenAlex
- Semantic Scholar

Features:

- DOI validation
- Metadata enrichment
- Citation verification
- Reference correction

### Compliance Engine

Checks:

- Journal requirements
- Section completeness
- Reference quality
- Formatting compliance

### Submission Package

Generate:

- Formatted Manuscript
- Reviewer Report
- Compliance Report
- DOI Report
- Cover Letter
- Conflict Statement

---

## 🛠️ Local Setup & Configuration

### 1. Backend Configuration (`/backend`)

Create a `.env` file in the `backend/` folder based on [.env.example](file:///d:/hakathonProjks/New%20folder/backend/.env.example):

```env
FIREBASE_PROJECT_ID=your-firebase-project-id
```

> [!TIP]
> **Developer Mock Auth Mode (Fast Local Testing)**
> If `FIREBASE_PROJECT_ID` is left empty, the backend operates in **Mock Auth Mode**. It prints a warning to stdout and accepts any token starting with `mock-` (e.g. `mock-user-token`) as a valid session. This allows you to run and test the codebase locally without creating a Firebase project.

#### Steps to Run:

1. Navigate to `/backend`:
   ```bash
   cd backend
   ```
2. Activate the virtual environment:
   - Windows (PowerShell): `.\venv\Scripts\Activate.ps1`
   - macOS/Linux: `source venv/bin/activate`
3. Run the development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   The backend API will be available at `http://localhost:8000`.

---

### 2. Frontend Configuration (`/frontend`)

Create a `.env.local` file in the `frontend/` folder based on [.env.local.example](file:///d:/hakathonProjks/New%20folder/frontend/.env.local.example):

```env
NEXT_PUBLIC_FIREBASE_API_KEY=your-api-key
NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
NEXT_PUBLIC_FIREBASE_PROJECT_ID=your-project-id
NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
NEXT_PUBLIC_FIREBASE_APP_ID=your-app-id
```

#### Steps to Run:

1. Navigate to `/frontend`:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   The app will start at `http://localhost:3000`.

---

## Architecture

```mermaid
flowchart LR

A[Upload] --> B[Extraction]

B --> C[DOCX ZIP/XML]
B --> D[PDF NLP/OCR]

C --> E[Canonical Manuscript]
D --> E

E --> F[AI Analysis]

F --> G[Reviewer AI]
F --> H[Compliance]
F --> I[DOI Intelligence]

G --> J[Formatting Studio]
H --> J
I --> J

J --> K[LaTeX Engine]

K --> L[Preview]
L --> M[Submission Package]
```

---

## Technology Stack

### Frontend

- Next.js 15
- TypeScript
- Tailwind CSS
- Framer Motion

### Backend

- FastAPI
- Python

### AI & NLP

- Gemini
- DeepSeek
- spaCy
- Sentence Transformers

### Citation Intelligence

- CrossRef
- OpenAlex
- Semantic Scholar

### Database

- PostgreSQL
- Supabase

### Authentication

- Firebase Authentication

### Formatting

- LaTeX
- IEEE Templates
- Elsevier Templates
- Custom Journal Templates

---

## Project Structure

```text
ThaalDraft/
│
├── frontend/
│   └── Next.js Application
│
├── backend/
│   └── FastAPI Services
│
├── docs/
│   ├── ARCHITECTURE_V2.md
│   ├── PRD_V2.md
│   ├── UI_UX_V2.md
│   └── ROADMAP_V2.md
│
└── database/
    └── DATABASE_SCHEMA_V2.sql
```

---

## Vision

Build a complete manuscript intelligence platform capable of transforming raw academic drafts into publication-ready journal submissions with minimal manual effort.
