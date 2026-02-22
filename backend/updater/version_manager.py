"""
Version manager — archives superseded NAAC documents before replacing them.
"""

import os
import shutil
from datetime import datetime, timezone


ARCHIVE_ROOT = "data/naac_requirements/_archive"


def archive_file(file_path: str) -> str:
    """
    Move *file_path* to the archive directory with a timestamp suffix.

    Returns the archive path.
    """
    if not os.path.exists(file_path):
        return ""

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    filename = os.path.basename(file_path)
    name, ext = os.path.splitext(filename)
    archived_name = f"{name}_{timestamp}{ext}"

    os.makedirs(ARCHIVE_ROOT, exist_ok=True)
    dest = os.path.join(ARCHIVE_ROOT, archived_name)
    shutil.move(file_path, dest)
    print(f"[version_manager] Archived {filename} → {dest}")
    return dest


def archive_if_exists(directory: str, filename: str) -> str:
    """Archive a file from a directory if it exists, then return the archive path."""
    candidate = os.path.join(directory, filename)
    if os.path.exists(candidate):
        return archive_file(candidate)
    return ""
