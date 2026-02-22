"""
PDF loader — extracts raw text from PDF files using pdfplumber.
"""

import os
from pathlib import Path
from typing import List, Dict, Any

try:
    import pdfplumber
except ImportError as exc:
    raise ImportError("pdfplumber is required: pip install pdfplumber") from exc


def load_pdf(file_path: str) -> str:
    """Extract all text from a PDF file."""
    text_parts: List[str] = []
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n".join(text_parts)


def load_pdfs_from_directory(directory: str) -> List[Dict[str, Any]]:
    """
    Recursively load all PDFs from a directory.

    Returns a list of dicts:
      { "file_path": str, "text": str, "filename": str }
    """
    results: List[Dict[str, Any]] = []
    for root, _, files in os.walk(directory):
        for fname in files:
            if fname.lower().endswith(".pdf"):
                fpath = os.path.join(root, fname)
                try:
                    text = load_pdf(fpath)
                    results.append(
                        {"file_path": fpath, "text": text, "filename": fname}
                    )
                except Exception as exc:
                    print(f"[pdf_loader] Warning: could not load {fpath}: {exc}")
    return results
