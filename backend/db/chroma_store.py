"""
ChromaDB store with two separate collections:
- naac_requirements: NAAC framework, SSR manual, criteria, guidelines
- mvsr_evidence:     MVSR institutional documents, policies, IQAC reports
"""

import chromadb
from chromadb.config import Settings

NAAC_COLLECTION = "naac_requirements"
MVSR_COLLECTION = "mvsr_evidence"
CHROMA_PATH = "./chroma_db"


def get_client() -> chromadb.PersistentClient:
    return chromadb.PersistentClient(
        path=CHROMA_PATH,
        settings=Settings(anonymized_telemetry=False),
    )


def get_naac_collection(client: chromadb.PersistentClient = None):
    c = client or get_client()
    return c.get_or_create_collection(
        name=NAAC_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def get_mvsr_collection(client: chromadb.PersistentClient = None):
    c = client or get_client()
    return c.get_or_create_collection(
        name=MVSR_COLLECTION,
        metadata={"hnsw:space": "cosine"},
    )


def get_both_collections():
    client = get_client()
    return get_naac_collection(client), get_mvsr_collection(client)
