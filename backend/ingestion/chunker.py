"""
Text chunker — splits long documents into overlapping chunks suitable for embedding.
"""

from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
) -> List[str]:
    """
    Split *text* into chunks of roughly *chunk_size* characters with
    *overlap* characters of context carried forward.

    Splitting is word-boundary aware to avoid mid-word cuts.
    """
    if not text or not text.strip():
        return []

    words = text.split()
    chunks: List[str] = []
    start = 0

    while start < len(words):
        end = start
        current_len = 0
        while end < len(words) and current_len + len(words[end]) + 1 <= chunk_size:
            current_len += len(words[end]) + 1
            end += 1

        if end == start:
            # single word longer than chunk_size — take it anyway
            end = start + 1

        chunk = " ".join(words[start:end])
        chunks.append(chunk)

        # advance by (chunk_size - overlap) worth of words
        overlap_words = 0
        overlap_len = 0
        for i in range(end - 1, start - 1, -1):
            overlap_len += len(words[i]) + 1
            if overlap_len >= overlap:
                break
            overlap_words += 1

        advance = max(1, (end - start) - overlap_words)
        start += advance

    return [c for c in chunks if c.strip()]
