from __future__ import annotations

import re


def normalize_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.strip().lower())


def split_into_chunks(text: str, chunk_size: int = 850, overlap: int = 120) -> list[str]:
    clean = re.sub(r"\n{3,}", "\n\n", text.strip())
    if len(clean) <= chunk_size:
        return [clean]

    chunks: list[str] = []
    start = 0
    while start < len(clean):
        end = min(start + chunk_size, len(clean))
        if end < len(clean):
            sentence_end = max(clean.rfind(".", start, end), clean.rfind("\n", start, end))
            if sentence_end > start + chunk_size // 2:
                end = sentence_end + 1
        chunks.append(clean[start:end].strip())
        next_start = end - overlap
        start = next_start if next_start > start else end
    return [chunk for chunk in chunks if chunk]
