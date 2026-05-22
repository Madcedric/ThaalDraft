from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import documents

app = FastAPI(title="ManuscriptAI API", version="0.1.0")

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

@app.get("/")
def root():
    return {"message": "ManuscriptAI API is running"}
