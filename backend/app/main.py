from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

# Load .env file from backend root
load_dotenv(Path(__file__).resolve().parent.parent / ".env")

from app.api.routes import documents, health, auth, exports, citations, compliance, reviewer, formatting, batch, submission, websockets

app = FastAPI(title="ThaalDraft API", version="0.1.0")

# Setup CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://thaaldraft.vercel.app",
        "https://thaaldraft-git-main.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(documents.router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(exports.router, prefix="/api/v1/documents", tags=["Exports"])
app.include_router(citations.router, prefix="/api/v1/documents", tags=["Citations"])
app.include_router(compliance.router, prefix="/api/v1/documents", tags=["Compliance"])
app.include_router(reviewer.router, prefix="/api/v1/documents", tags=["Reviewer"])
app.include_router(formatting.router, prefix="/api/v1/documents", tags=["Formatting"])
app.include_router(batch.router, prefix="/api/v1", tags=["Batch"])
app.include_router(submission.router, prefix="/api/v1/documents", tags=["Submission"])
app.include_router(websockets.router, prefix="", tags=["WebSockets"])

@app.get("/")
def root():
    return {"message": "ThaalDraft API is running"}
