"""
Ollama LLM client — wraps the local Ollama REST API for llama3.
"""

import json
import urllib.request
from typing import Generator

OLLAMA_BASE_URL = "http://localhost:11434"
DEFAULT_MODEL = "llama3"


def generate(prompt: str, model: str = DEFAULT_MODEL, stream: bool = False) -> str:
    """
    Send a prompt to Ollama and return the complete response string.
    """
    payload = json.dumps({"model": model, "prompt": prompt, "stream": stream}).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = resp.read().decode()

    if stream:
        # stream=False above, but handle just in case
        return body

    data = json.loads(body)
    return data.get("response", "")


def health_check() -> bool:
    """Return True if Ollama is reachable."""
    try:
        req = urllib.request.Request(f"{OLLAMA_BASE_URL}/api/tags", method="GET")
        with urllib.request.urlopen(req, timeout=5):
            return True
    except Exception:
        return False
