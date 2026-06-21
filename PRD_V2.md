# ThaalDraft V2 PRD (Product Requirements Document)

## Goal
Transform the ThaalDraft MVP into a SaaS-grade manuscript preparation platform that reliably processes raw drafts and formats them into publication-ready packages, eliminating current reliability issues and adding advanced AI and DOI intelligence.

## Target Audience
Researchers, Academics, PhD Students, and Postdocs who need to format papers for journals (IEEE, ACM, Springer, Elsevier, etc.) but lack the time or LaTeX expertise.

## Core Modes
1. **Reconstruction Mode**: Handles messy drafts and incomplete papers. The system extracts raw text, structure, and citations, then uses AI to reconstruct a canonical manuscript.
2. **Formatting Studio**: Handles already-structured manuscripts and applies journal-specific templates (LaTeX and DOCX generation).

## Key Features
- **Intelligent Extraction**: Native DOCX (ZIP/XML) and PDF (NLP/OCR) parsing.
- **AI-Powered Review**: Uses Gemini and DeepSeek for structural review and compliance checking.
- **Citation Intelligence**: Validates references against CrossRef, OpenAlex, and Semantic Scholar. Detects duplicates and broken links.
- **Real-Time Workspace**: A split-screen UI showing document structure on the left, live manuscript in the center, and AI analysis on the right.
- **Submission Packaging**: Generates a complete ZIP file containing the formatted manuscript, figures, and supplementary materials.

## Non-Functional Requirements
- **Performance**: Single file processing < 30 seconds. Batch processing (100 files) < 5 minutes.
- **Reliability**: Asynchronous processing with automatic retries and clear error states. No silent failures.
- **Accuracy**: Parsing > 95%, Citation Validation > 95%, Formatting > 98%.
- **Mobile Support**: The web app must be fully responsive for mobile and tablet devices.
