"""
Ingestion orchestrator — loads PDFs, chunks them, embeds, and stores in ChromaDB.

Directory conventions
---------------------
  data/naac_requirements/criterion_<N>/  → type=requirement, criterion inferred from folder
  data/mvsr_evidence/<category>/         → type=evidence, category inferred from folder
"""

import os
import re
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional

from sentence_transformers import SentenceTransformer

from backend.ingestion.pdf_loader import load_pdfs_from_directory
from backend.ingestion.chunker import chunk_text
from backend.db.chroma_store import get_naac_collection, get_mvsr_collection

EMBED_MODEL = "all-MiniLM-L6-v2"
_embedder: Optional[SentenceTransformer] = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def _embed(texts: List[str]) -> List[List[float]]:
    return _get_embedder().encode(texts, show_progress_bar=False).tolist()


def _infer_criterion(path: str) -> str:
    """Extract criterion number from directory name like criterion_2."""
    match = re.search(r"criterion[_\-]?(\w+)", path, re.IGNORECASE)
    return match.group(1) if match else "unknown"


def ingest_naac_documents(directory: str, version: str = "2025") -> int:
    """Ingest NAAC requirement documents from *directory* into ChromaDB."""
    collection = get_naac_collection()
    docs = load_pdfs_from_directory(directory)
    total = 0

    for doc in docs:
        criterion = _infer_criterion(doc["file_path"])
        chunks = chunk_text(doc["text"])
        if not chunks:
            continue

        ids = [str(uuid.uuid4()) for _ in chunks]
        embeddings = _embed(chunks)
        metadatas = [
            {
                "type": "requirement",
                "criterion": criterion,
                "indicator": "",
                "version": version,
                "status": "active",
                "source_file": doc["filename"],
            }
            for _ in chunks
        ]

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
        total += len(chunks)
        print(f"[ingest] NAAC  {doc['filename']}: {len(chunks)} chunks")

    return total


def ingest_mvsr_documents(directory: str, year: int = 2024) -> int:
    """Ingest MVSR evidence documents from *directory* into ChromaDB."""
    collection = get_mvsr_collection()
    docs = load_pdfs_from_directory(directory)
    total = 0

    for doc in docs:
        # derive category from the last meaningful directory component
        category = Path(doc["file_path"]).parent.name
        chunks = chunk_text(doc["text"])
        if not chunks:
            continue

        ids = [str(uuid.uuid4()) for _ in chunks]
        embeddings = _embed(chunks)
        metadatas = [
            {
                "type": "evidence",
                "criterion": "",
                "document": doc["filename"],
                "category": category,
                "year": year,
                "source_file": doc["filename"],
            }
            for _ in chunks
        ]

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=chunks,
            metadatas=metadatas,
        )
        total += len(chunks)
        print(f"[ingest] MVSR  {doc['filename']}: {len(chunks)} chunks")

    return total


def run_full_ingestion(
    naac_dir: str = "data/naac_requirements",
    mvsr_dir: str = "data/mvsr_evidence",
    naac_version: str = "2025",
    mvsr_year: int = 2024,
) -> Dict[str, int]:
    """Ingest both NAAC and MVSR document sets."""
    naac_count = ingest_naac_documents(naac_dir, version=naac_version)
    mvsr_count = ingest_mvsr_documents(mvsr_dir, year=mvsr_year)
    return {"naac_chunks": naac_count, "mvsr_chunks": mvsr_count}
