"""
NAAC website watcher — polls the NAAC website for new/changed documents.

Detection strategy:
  1. Fetch the target page HTML.
  2. Extract document links (PDF / DOC).
  3. Compare checksums against the last-known snapshot.
  4. Return a list of changed/new document URLs.
"""

import hashlib
import json
import os
import urllib.request
from typing import List, Dict, Any
from html.parser import HTMLParser

SNAPSHOT_FILE = "data/naac_requirements/.snapshot.json"
NAAC_BASE_URL = "https://www.naac.gov.in"
NAAC_WATCH_URLS = [
    "https://www.naac.gov.in/index.php/en/ssr-manuals",
    "https://www.naac.gov.in/index.php/en/assessment-accreditation/guidelines",
]


class _LinkExtractor(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links: List[str] = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            attrs_dict = dict(attrs)
            href = attrs_dict.get("href", "")
            if href.lower().endswith((".pdf", ".doc", ".docx")):
                self.links.append(href)


def _page_hash(url: str) -> str:
    """Fetch a URL and return an MD5 hash of its content."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "NAAC-Watcher/1.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            return hashlib.md5(resp.read()).hexdigest()
    except Exception as exc:
        print(f"[naac_watcher] Could not fetch {url}: {exc}")
        return ""


def _load_snapshot() -> Dict[str, str]:
    if os.path.exists(SNAPSHOT_FILE):
        with open(SNAPSHOT_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_snapshot(snapshot: Dict[str, str]) -> None:
    os.makedirs(os.path.dirname(SNAPSHOT_FILE), exist_ok=True)
    with open(SNAPSHOT_FILE, "w") as f:
        json.dump(snapshot, f, indent=2)


def check_for_updates() -> List[str]:
    """
    Compare current page hashes against stored snapshot.

    Returns a list of URLs whose content has changed (or are new).
    """
    snapshot = _load_snapshot()
    changed: List[str] = []

    for url in NAAC_WATCH_URLS:
        current_hash = _page_hash(url)
        if not current_hash:
            continue
        if snapshot.get(url) != current_hash:
            changed.append(url)
            snapshot[url] = current_hash

    _save_snapshot(snapshot)
    return changed


def extract_document_links(page_url: str) -> List[str]:
    """Extract PDF/DOC links from an NAAC page."""
    try:
        req = urllib.request.Request(
            page_url, headers={"User-Agent": "NAAC-Watcher/1.0"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as exc:
        print(f"[naac_watcher] Could not fetch {page_url}: {exc}")
        return []

    parser = _LinkExtractor()
    parser.feed(html)

    links = []
    for href in parser.links:
        if href.startswith("http"):
            links.append(href)
        else:
            links.append(NAAC_BASE_URL + "/" + href.lstrip("/"))
    return links
