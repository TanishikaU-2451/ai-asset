"""
LLM response generator — builds a structured compliance answer from retrieved
context using the local Ollama llama3 model.
"""

from typing import List, Dict, Any

from backend.llm.ollama_client import generate


_PROMPT_TEMPLATE = """You are an expert NAAC compliance analyst for MVSR Engineering College.

Your task is to answer the user's query by reasoning over the provided context.
Do NOT use any pre-defined templates or keyword matching. Generate your response
entirely from the context below.

USER QUERY:
{query}

NAAC REQUIREMENT CONTEXT (retrieved from official NAAC documents):
{naac_context}

MVSR EVIDENCE CONTEXT (retrieved from MVSR institutional documents):
{mvsr_context}

Provide a structured answer in the following format:

NAAC REQUIREMENT:
(Summarise what NAAC expects based on the context)

MVSR EVIDENCE:
(Describe what MVSR has implemented based on the context)

COMPLIANCE ANALYSIS:
(Analyse whether MVSR satisfies the NAAC requirement. Be specific and evidence-based.)
"""


def _format_context(results: List[Dict[str, Any]], max_chars: int = 3000) -> str:
    parts = []
    total = 0
    for item in results:
        text = item.get("text", "").strip()
        if not text:
            continue
        meta = item.get("metadata", {})
        header = (
            f"[Source: {meta.get('source_file', 'unknown')} | "
            f"Criterion: {meta.get('criterion', 'N/A')} | "
            f"Type: {meta.get('type', 'N/A')}]"
        )
        entry = f"{header}\n{text}"
        if total + len(entry) > max_chars:
            break
        parts.append(entry)
        total += len(entry)
    return "\n\n".join(parts) if parts else "No relevant context found."


def generate_response(
    query: str,
    naac_results: List[Dict[str, Any]],
    mvsr_results: List[Dict[str, Any]],
    model: str = "llama3",
) -> str:
    """Generate a structured compliance answer via Ollama."""
    naac_ctx = _format_context(naac_results)
    mvsr_ctx = _format_context(mvsr_results)

    prompt = _PROMPT_TEMPLATE.format(
        query=query,
        naac_context=naac_ctx,
        mvsr_context=mvsr_ctx,
    )

    return generate(prompt, model=model)
