from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.config import POLICY_DIR


@dataclass(frozen=True)
class Document:
    source: str
    text: str


def load_documents(policy_dir: Path = POLICY_DIR) -> list[Document]:
    documents = []
    for path in sorted(policy_dir.glob("*.txt")):
        documents.append(Document(source=path.name, text=path.read_text(encoding="utf-8")))
    return documents
