"""
FastAPI application — NAAC Compliance Intelligence System for MVSR Engineering College.

Endpoints:
  POST /ingest        — Ingest NAAC + MVSR documents from default data directories.
  POST /query         — Run a RAG compliance query.
  POST /force-update  — Trigger an immediate NAAC update cycle.
  GET  /health        — Health check (Ollama + ChromaDB status).
  GET  /last-sync     — Return the last NAAC sync timestamp and stats.
"""

from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.rag.pipeline import run_pipeline
from backend.ingestion.ingest import run_full_ingestion
from backend.scheduler.update_scheduler import (
    get_last_sync,
    run_update_cycle,
    start_scheduler,
    stop_scheduler,
)
from backend.llm.ollama_client import health_check as ollama_health
from backend.db.chroma_store import get_both_collections


# ---------------------------------------------------------------------------
# Lifespan — start / stop background scheduler
# ---------------------------------------------------------------------------

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(
    title="NAAC Compliance Intelligence System",
    description=(
        "RAG-based compliance assistant for MVSR Engineering College. "
        "Retrieves NAAC requirements and MVSR institutional evidence to "
        "generate structured compliance answers."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Request / Response schemas
# ---------------------------------------------------------------------------

class QueryRequest(BaseModel):
    query: str
    n_naac: int = 4
    n_mvsr: int = 4
    model: str = "llama3"


class QueryResponse(BaseModel):
    answer: str
    naac_requirement: str
    mvsr_evidence: str
    naac_mapping: str
    status: str


class IngestRequest(BaseModel):
    naac_dir: str = "data/naac_requirements"
    mvsr_dir: str = "data/mvsr_evidence"
    naac_version: str = "2025"
    mvsr_year: int = 2024


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------

@app.post("/query", response_model=QueryResponse)
async def query_endpoint(body: QueryRequest):
    """
    Run a semantic RAG compliance query.

    Retrieves NAAC requirements and MVSR evidence, then generates a
    structured answer using the local Ollama LLM.
    """
    try:
        result = run_pipeline(
            query=body.query,
            n_naac=body.n_naac,
            n_mvsr=body.n_mvsr,
            model=body.model,
        )
        return QueryResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/ingest")
async def ingest_endpoint(body: IngestRequest):
    """
    Ingest NAAC requirement and MVSR evidence documents into ChromaDB.

    Processes all PDFs found recursively under the specified directories.
    """
    try:
        counts = run_full_ingestion(
            naac_dir=body.naac_dir,
            mvsr_dir=body.mvsr_dir,
            naac_version=body.naac_version,
            mvsr_year=body.mvsr_year,
        )
        return {"status": "ok", **counts}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/force-update")
async def force_update_endpoint():
    """
    Immediately trigger a full NAAC document update cycle (normally daily).

    Checks the NAAC website for changes, downloads new documents, archives
    old versions, and re-ingests updated content into ChromaDB.
    """
    try:
        result = run_update_cycle()
        return {"status": "ok", **result}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.get("/health")
async def health_endpoint():
    """Return the health status of dependent services."""
    ollama_ok = ollama_health()

    chroma_ok = False
    chroma_counts = {}
    try:
        naac_col, mvsr_col = get_both_collections()
        chroma_counts["naac_chunks"] = naac_col.count()
        chroma_counts["mvsr_chunks"] = mvsr_col.count()
        chroma_ok = True
    except Exception as exc:
        chroma_counts["error"] = str(exc)

    return {
        "status": "ok" if (ollama_ok and chroma_ok) else "degraded",
        "ollama": "up" if ollama_ok else "down",
        "chromadb": "up" if chroma_ok else "down",
        **chroma_counts,
    }


@app.get("/last-sync")
async def last_sync_endpoint():
    """Return the timestamp and statistics from the last NAAC document sync."""
    return get_last_sync()
