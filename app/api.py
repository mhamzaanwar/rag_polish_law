"""
FastAPI backend — exposes the RAG pipeline as a REST API.

Run: uvicorn app.api:app --reload

This is OPTIONAL but makes the demo more impressive — clients see you can
ship both a UI and an API, which matters for SaaS-integration projects.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from app.rag import get_pipeline

app = FastAPI(
    title="Polish Business Law RAG API",
    description="Answers questions about Polish business law with source citations.",
    version="1.0.0",
)

# CORS so the API can be called from any frontend during the demo
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class QueryRequest(BaseModel):
    question: str = Field(..., min_length=3, max_length=500, examples=["What's the VAT threshold?"])


class SourceRef(BaseModel):
    name: str
    preview: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceRef]
    latency_ms: int
    tokens_used: int | None = None


@app.on_event("startup")
def warmup():
    """Load the index at startup, not on first request."""
    try:
        get_pipeline()
    except Exception as e:
        print(f"WARNING: pipeline failed to load at startup: {e}")


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(req: QueryRequest):
    try:
        pipeline = get_pipeline()
        resp = pipeline.query(req.question)
        return QueryResponse(
            answer=resp.answer,
            sources=[SourceRef(**s) for s in resp.sources],
            latency_ms=resp.latency_ms,
            tokens_used=resp.tokens_used,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/Hamza")
def Hamza():
    return {"status": "ok"}