from __future__ import annotations

import re


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    section_chunks = chunk_by_policy_sections(text)
    if section_chunks:
        return section_chunks

    chunks: list[str] = []
    start = 0
    clean = text.strip()
    while start < len(clean):
        end = min(start + chunk_size, len(clean))
        if end < len(clean):
            boundary = max(clean.rfind(".", start, end), clean.rfind("\n", start, end), clean.rfind(" ", start, end))
            if boundary > start + chunk_size // 2:
                end = boundary + 1
        chunks.append(clean[start:end].strip())
        next_start = end - overlap
        start = next_start if next_start > start else end
    return [chunk for chunk in chunks if chunk]


def chunk_by_policy_sections(text: str) -> list[str]:
    clean = text.strip()
    title_match = re.search(r"^Policy Title:\s*(.+)$", clean, flags=re.MULTILINE)
    policy_id_match = re.search(r"^Policy ID:\s*(.+)$", clean, flags=re.MULTILINE)
    title = title_match.group(1).strip() if title_match else "Hospital Policy"
    policy_id = policy_id_match.group(1).strip() if policy_id_match else ""

    headings = [
        "Purpose",
        "Scope",
        "Responsibilities",
        "Procedure",
        "Exceptions",
        "Escalation Process",
        "Review Date",
    ]
    chunks: list[str] = []
    for index, heading in enumerate(headings):
        next_heading = headings[index + 1] if index + 1 < len(headings) else None
        if next_heading:
            pattern = rf"{heading}:\s*(.*?)(?=\n\n{next_heading}:)"
        else:
            pattern = rf"{heading}:\s*(.*)$"
        match = re.search(pattern, clean, flags=re.DOTALL)
        if match:
            body = match.group(1).strip()
            chunks.append(f"Policy Title: {title}\nPolicy ID: {policy_id}\nSection: {heading}\n{body}")
    return chunks
