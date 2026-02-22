"""
APScheduler-based daily scheduler for NAAC document updates.

Runs the full update cycle once per day:
  1. Check NAAC pages for changes (naac_watcher)
  2. Extract and download new documents (downloader)
  3. Archive old versions (version_manager)
  4. Ingest new documents into ChromaDB (auto_ingest)
"""

import json
import os
from datetime import datetime, timezone
from typing import Any, Dict

from typing import Any, Dict, Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from backend.updater.naac_watcher import check_for_updates, extract_document_links
from backend.updater.downloader import download_documents
from backend.updater.auto_ingest import ingest_files

SYNC_STATE_FILE = "data/.last_sync.json"

_scheduler: Optional[BackgroundScheduler] = None


def _load_sync_state() -> Dict[str, Any]:
    if os.path.exists(SYNC_STATE_FILE):
        with open(SYNC_STATE_FILE, "r") as f:
            return json.load(f)
    return {"last_sync": None, "documents_processed": 0}


def _save_sync_state(state: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(SYNC_STATE_FILE), exist_ok=True)
    with open(SYNC_STATE_FILE, "w") as f:
        json.dump(state, f, indent=2)


def run_update_cycle() -> Dict[str, Any]:
    """
    Execute a full NAAC update cycle.

    Returns a summary dict with the sync timestamp and counts.
    """
    print("[scheduler] Starting NAAC update cycle …")
    changed_pages = check_for_updates()
    all_doc_urls = []

    for page_url in changed_pages:
        links = extract_document_links(page_url)
        all_doc_urls.extend(links)

    downloaded_paths = download_documents(all_doc_urls) if all_doc_urls else []
    valid_paths = [p for p in downloaded_paths if p]
    chunks_added = ingest_files(valid_paths) if valid_paths else 0

    state = {
        "last_sync": datetime.now(timezone.utc).isoformat(),
        "pages_checked": len(changed_pages),
        "documents_downloaded": len(valid_paths),
        "chunks_added": chunks_added,
    }
    _save_sync_state(state)
    print(f"[scheduler] Update cycle complete: {state}")
    return state


def get_last_sync() -> Dict[str, Any]:
    """Return the last sync state."""
    return _load_sync_state()


def start_scheduler() -> None:
    """Start the background daily scheduler."""
    global _scheduler
    if _scheduler is not None and _scheduler.running:
        return

    _scheduler = BackgroundScheduler(daemon=True)
    _scheduler.add_job(
        run_update_cycle,
        trigger=CronTrigger(hour=2, minute=0),  # run at 02:00 UTC daily
        id="naac_daily_update",
        replace_existing=True,
    )
    _scheduler.start()
    print("[scheduler] Daily NAAC update scheduler started (02:00 UTC).")


def stop_scheduler() -> None:
    """Stop the background scheduler gracefully."""
    global _scheduler
    if _scheduler and _scheduler.running:
        _scheduler.shutdown(wait=False)
        print("[scheduler] Scheduler stopped.")
