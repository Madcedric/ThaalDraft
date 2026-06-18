from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import documents, health, auth, exports, citations

app = FastAPI(title="ThaalDraft API", version="0.1.0")

# Setup CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
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

@app.get("/")
def root():
    return {"message": "ThaalDraft API is running"}
