"""
RAG pipeline — orchestrates retrieval → metadata mapping → generation.

Query Flow:
  User Query
      ↓ Semantic Embedding
      ↓ Vector Retrieval (NAAC + MVSR collections)
      ↓ Dynamic Metadata Mapping (criterion / status)
      ↓ Context-based LLM Reasoning
      ↓ Structured Response
"""

from typing import Dict, Any

from backend.rag.retriever import retrieve
from backend.rag.generator import generate_response
from backend.rag.metadata_mapper import infer_naac_mapping, infer_compliance_status


def run_pipeline(
    query: str,
    n_naac: int = 4,
    n_mvsr: int = 4,
    model: str = "llama3",
) -> Dict[str, Any]:
    """
    Run the full RAG pipeline for a compliance query.

    Parameters
    ----------
    query   : Natural-language question from the user.
    n_naac  : Number of NAAC chunks to retrieve.
    n_mvsr  : Number of MVSR chunks to retrieve.
    model   : Ollama model name.

    Returns
    -------
    {
        "answer":           str,   # full LLM answer
        "naac_requirement": str,   # top NAAC snippet
        "mvsr_evidence":    str,   # top MVSR snippet
        "naac_mapping":     str,   # dynamically inferred criterion label
        "status":           str,   # Supported / Partially Supported / Gap Identified
    }
    """
    retrieved = retrieve(query, n_naac=n_naac, n_mvsr=n_mvsr)
    naac_results = retrieved["naac_results"]
    mvsr_results = retrieved["mvsr_results"]

    naac_mapping = infer_naac_mapping(naac_results)
    status = infer_compliance_status(naac_results, mvsr_results)

    answer = generate_response(query, naac_results, mvsr_results, model=model)

    naac_snippet = naac_results[0]["text"][:500] if naac_results else ""
    mvsr_snippet = mvsr_results[0]["text"][:500] if mvsr_results else ""

    return {
        "answer": answer,
        "naac_requirement": naac_snippet,
        "mvsr_evidence": mvsr_snippet,
        "naac_mapping": naac_mapping,
        "status": status,
    }
