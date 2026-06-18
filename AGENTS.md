# ThaalDraft - Agent Rules

## Project Context

This project is an existing application.

The objective is to transform it into a SaaS-grade ThaalDraft.

The project must evolve through:

Audit → Refactor → Build → Validate → Deploy

Do not rebuild from scratch.

---

# Current Stack

Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Shadcn UI

Backend

- FastAPI
- Python

Authentication

- Firebase Auth

Database

- Supabase PostgreSQL

Storage

- Supabase Storage

Frontend Deployment

- Vercel

Backend Deployment

- Render

---

# AI Stack

Use only open-source models whenever possible.

Preferred:

- Ollama
- Qwen
- Llama 3
- Sentence Transformers
- SciBERT
- spaCy

Avoid paid APIs unless explicitly approved.

---

# External Sources

Allowed

- OpenAlex
- CrossRef
- Semantic Scholar

Avoid commercial research APIs.

---

# Development Rules

Always:

1. Audit before modifying.
2. Refactor before replacing.
3. Reuse existing code whenever possible.
4. Preserve working functionality.
5. Maintain backward compatibility.
6. Keep code modular.
7. Keep services isolated.

Never:

1. Rewrite the entire project.
2. Modify unrelated files.
3. Introduce unnecessary dependencies.
4. Implement future phases without approval.
5. Replace working functionality without justification.

---

# Phase Execution Rules

For every phase:

Step 1

Analyze current implementation.

Step 2

Generate implementation plan.

Step 3

Implement changes.

Step 4

Run validation.

Step 5

Run build checks.

Step 6

Fix issues.

Step 7

Generate completion report.

Step 8

Commit changes.

Step 9

Push to GitHub.

Step 10

Wait for approval.

Do not automatically continue.

---

# Commit Format

feat(phase-x): description

Examples:

feat(phase-0): architecture audit

feat(phase-1): architecture refactor

feat(phase-4): citation intelligence engine

fix(upload): resolve pdf parsing issue

---

# UI Rules

The application must resemble a premium SaaS platform.

Design Inspiration:

- Notion
- Linear
- Grammarly
- Overleaf

Requirements:

- Clean
- Minimal
- Modern
- Accessible
- Fast

Avoid:

- Generic admin dashboards
- Excessive tables
- Complex navigation
- Visual clutter

---

# Mobile Requirements

Every feature must support:

- Mobile
- Tablet
- Desktop

Use responsive layouts.

Use touch-friendly interactions.

No desktop-only functionality.

---

# AI Usage Policy

Priority Order

1. Deterministic Logic
2. NLP Models
3. Embeddings
4. LLM

Use LLMs only when deterministic solutions are insufficient.

Formatting must never rely on LLM output.

Citation validation must never rely on LLM output.

Compliance checking must never rely on LLM output.

---

# Accuracy Requirements

Target:

- Parsing Accuracy > 95%
- Citation Validation Accuracy > 95%
- Formatting Accuracy > 98%
- Compliance Accuracy > 95%

Use rule-based systems whenever possible.

---

# Performance Requirements

Target Processing Time

Single File:

< 30 seconds

Batch Processing:

< 5 minutes for 100 files

Optimize for scalability.

---

# GitHub Workflow

Every completed phase must:

1. Pass build validation.
2. Pass lint checks.
3. Pass type checks.
4. Be committed.
5. Be pushed.

Generate:

- Files Changed
- Risks
- Recommendations
- Next Steps

Wait for approval before continuing.

---

# Final Rule

The agent must think like a senior software architect.

Prioritize:

Reliability
Maintainability
Scalability
Accuracy
Cost Efficiency

over rapid feature generation.
