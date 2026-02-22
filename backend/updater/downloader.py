"""
Document downloader — downloads NAAC PDF/DOC files and saves them to the
appropriate criterion directory under data/naac_requirements/.
"""

import os
import re
import urllib.request
from pathlib import Path
from typing import Optional

NAAC_REQUIREMENTS_DIR = "data/naac_requirements"
DEFAULT_CRITERION_DIR = "data/naac_requirements/criterion_general"


def _guess_criterion_dir(url: str, filename: str) -> str:
    """
    Infer which criterion directory to save the file in based on URL/filename.
    Falls back to criterion_general.
    """
    combined = (url + filename).lower()
    match = re.search(r"criterion[_\-\s]?(\d+)", combined)
    if match:
        return os.path.join(NAAC_REQUIREMENTS_DIR, f"criterion_{match.group(1)}")
    return DEFAULT_CRITERION_DIR


def download_document(url: str, dest_dir: Optional[str] = None) -> Optional[str]:
    """
    Download a document from *url* and save it locally.

    Parameters
    ----------
    url      : Full URL of the document.
    dest_dir : Override directory; if None, it is inferred from the URL.

    Returns
    -------
    Absolute path of the saved file, or None on failure.
    """
    filename = os.path.basename(url.split("?")[0]) or "document.pdf"
    if dest_dir is None:
        dest_dir = _guess_criterion_dir(url, filename)

    os.makedirs(dest_dir, exist_ok=True)
    dest_path = os.path.join(dest_dir, filename)

    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NAAC-Downloader/1.0"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            with open(dest_path, "wb") as f:
                f.write(resp.read())
        print(f"[downloader] Saved {filename} → {dest_path}")
        return dest_path
    except Exception as exc:
        print(f"[downloader] Failed to download {url}: {exc}")
        return None


def download_documents(urls: list) -> list:
    """Download multiple documents; returns list of saved paths (None for failures)."""
    return [download_document(url) for url in urls]
