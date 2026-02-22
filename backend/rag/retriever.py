"""
Dual-collection semantic retriever.

Uses sentence-transformers embeddings to perform cosine similarity search
against two separate ChromaDB collections (NAAC requirements and MVSR evidence).
"""

from typing import List, Dict, Any, Optional

from sentence_transformers import SentenceTransformer

from backend.db.chroma_store import get_both_collections

EMBED_MODEL = "all-MiniLM-L6-v2"
_embedder: Optional[SentenceTransformer] = None


def _get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformer(EMBED_MODEL)
    return _embedder


def _embed_query(query: str) -> List[float]:
    return _get_embedder().encode([query], show_progress_bar=False)[0].tolist()


def retrieve(
    query: str,
    n_naac: int = 4,
    n_mvsr: int = 4,
) -> Dict[str, Any]:
    """
    Retrieve top-k results from both collections for the given natural-language query.

    Returns
    -------
    {
        "naac_results": [ {"text": ..., "metadata": ...}, ... ],
        "mvsr_results": [ {"text": ..., "metadata": ...}, ... ],
    }
    """
    embedding = _embed_query(query)
    naac_col, mvsr_col = get_both_collections()

    def _query_collection(collection, n_results: int):
        try:
            result = collection.query(
                query_embeddings=[embedding],
                n_results=n_results,
                include=["documents", "metadatas", "distances"],
            )
            items = []
            docs = result.get("documents", [[]])[0]
            metas = result.get("metadatas", [[]])[0]
            dists = result.get("distances", [[]])[0]
            for doc, meta, dist in zip(docs, metas, dists):
                items.append(
                    {"text": doc, "metadata": meta, "distance": dist}
                )
            return items
        except Exception as exc:
            print(f"[retriever] Warning during query: {exc}")
            return []

    naac_results = _query_collection(naac_col, n_naac)
    mvsr_results = _query_collection(mvsr_col, n_mvsr)

    return {"naac_results": naac_results, "mvsr_results": mvsr_results}
