"""
Auto-ingest trigger — called after new NAAC documents are downloaded.

Embeds and upserts only the newly downloaded files into ChromaDB without
re-processing the entire corpus.
"""

import os
import uuid
from typing import List, Optional

from sentence_transformers import SentenceTransformer

from backend.ingestion.pdf_loader import load_pdf
from backend.ingestion.chunker import chunk_text
from backend.db.chroma_store import get_naac_collection

EMBED_MODEL = "all-MiniLM-L6-v2"
_embedder: Optional[SentenceTransformer] = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def ingest_file(file_path: str, version: str = "latest") -> int:
    """
    Ingest a single PDF file into the NAAC requirements collection.

    Returns the number of chunks added.
    """
    if not os.path.exists(file_path):
        print(f"[auto_ingest] File not found: {file_path}")
        return 0

    try:
        text = load_pdf(file_path)
    except Exception as exc:
        print(f"[auto_ingest] Could not read {file_path}: {exc}")
        return 0

    chunks = chunk_text(text)
    if not chunks:
        return 0

    embedder = _get_embedder()
    embeddings = embedder.encode(chunks, show_progress_bar=False).tolist()
    collection = get_naac_collection()

    ids = [str(uuid.uuid4()) for _ in chunks]
    metadatas = [
        {
            "type": "requirement",
            "criterion": "unknown",
            "indicator": "",
            "version": version,
            "status": "active",
            "source_file": os.path.basename(file_path),
        }
        for _ in chunks
    ]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=chunks,
        metadatas=metadatas,
    )
    print(f"[auto_ingest] Ingested {os.path.basename(file_path)}: {len(chunks)} chunks")
    return len(chunks)


def ingest_files(file_paths: List[str], version: str = "latest") -> int:
    """Ingest multiple files; returns total chunks added."""
    return sum(ingest_file(fp, version=version) for fp in file_paths if fp)
