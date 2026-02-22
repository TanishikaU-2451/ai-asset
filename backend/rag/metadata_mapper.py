"""
Dynamic metadata mapper — infers NAAC criterion and compliance status purely
from the retrieved context metadata (no hard-coded if/else logic).
"""

from typing import List, Dict, Any


def infer_naac_mapping(naac_results: List[Dict[str, Any]]) -> str:
    """
    Dynamically derive a NAAC criterion mapping string from retrieval metadata.

    Aggregates criterion values from all retrieved NAAC chunks, picks the most
    frequent one, and formats a human-readable label.
    """
    if not naac_results:
        return "Unknown"

    counts: Dict[str, int] = {}
    for item in naac_results:
        meta = item.get("metadata", {})
        criterion = meta.get("criterion", "")
        indicator = meta.get("indicator", "")
        if criterion:
            key = f"Criterion {criterion}"
            if indicator:
                key += f".{indicator}"
            counts[key] = counts.get(key, 0) + 1

    if not counts:
        return "Unknown"

    return max(counts, key=lambda k: counts[k])


def infer_compliance_status(
    naac_results: List[Dict[str, Any]],
    mvsr_results: List[Dict[str, Any]],
) -> str:
    """
    Determine compliance status based solely on the presence and proximity of
    retrieved evidence — no keyword or template matching.

    Logic:
    - If strong MVSR evidence exists (low distance / high similarity) → Supported
    - If MVSR evidence exists but is weak → Partial
    - If no MVSR evidence → Gap Identified
    """
    if not mvsr_results:
        return "Gap Identified"

    # ChromaDB cosine distance: 0 = identical, 1 = orthogonal, 2 = opposite
    best_distance = min(item.get("distance", 2.0) for item in mvsr_results)

    if best_distance < 0.5:
        return "Supported"
    if best_distance < 0.85:
        return "Partially Supported"
    return "Gap Identified"
