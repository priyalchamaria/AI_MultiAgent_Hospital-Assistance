from __future__ import annotations

import pickle
from dataclasses import dataclass
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.config import POLICY_DIR, RAG_INDEX_PATH
from src.policy_generator import ensure_policy_documents
from src.text_utils import split_into_chunks


@dataclass
class RetrievedChunk:
    source: str
    score: float
    text: str


@dataclass
class RAGAgentResult:
    answer: str
    citations: list[RetrievedChunk]
    explanation: str


class RAGAgent:
    """Retrieval-augmented policy-document agent using a local TF-IDF index."""

    def __init__(self, policy_dir: Path = POLICY_DIR, index_path: Path = RAG_INDEX_PATH) -> None:
        self.policy_dir = policy_dir
        self.index_path = index_path
        self.vectorizer: TfidfVectorizer | None = None
        self.matrix = None
        self.chunks: list[dict[str, str]] = []
        self._load_or_build()

    def answer(self, query: str, top_k: int = 3) -> RAGAgentResult:
        if not self.chunks or self.matrix is None or self.vectorizer is None:
            return RAGAgentResult(
                answer="No policy documents are available. Run scripts/prepare_data.py first.",
                citations=[],
                explanation="The RAG index is empty.",
            )

        query_vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(query_vector, self.matrix).flatten()
        ranked_indexes = similarities.argsort()[::-1][:top_k]
        citations = [
            RetrievedChunk(
                source=self.chunks[index]["source"],
                score=round(float(similarities[index]), 3),
                text=self.chunks[index]["text"],
            )
            for index in ranked_indexes
            if similarities[index] > 0
        ]

        if not citations:
            return RAGAgentResult(
                answer="I could not find a matching hospital policy passage for that question.",
                citations=[],
                explanation="No retrieved chunk had a positive similarity score.",
            )

        answer = self._compose_answer(citations)
        return RAGAgentResult(
            answer=answer,
            citations=citations,
            explanation=f"Retrieved {len(citations)} relevant policy chunk(s) using TF-IDF cosine similarity.",
        )

    def rebuild(self) -> None:
        ensure_policy_documents(self.policy_dir)
        self.chunks = []
        for path in sorted(self.policy_dir.glob("*.md")):
            text = path.read_text(encoding="utf-8")
            for chunk in split_into_chunks(text):
                self.chunks.append({"source": path.name, "text": chunk})
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform([chunk["text"] for chunk in self.chunks])
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with self.index_path.open("wb") as file:
            pickle.dump(
                {"chunks": self.chunks, "vectorizer": self.vectorizer, "matrix": self.matrix},
                file,
            )

    def _load_or_build(self) -> None:
        if self.index_path.exists():
            with self.index_path.open("rb") as file:
                payload = pickle.load(file)
            self.chunks = payload["chunks"]
            self.vectorizer = payload["vectorizer"]
            self.matrix = payload["matrix"]
        else:
            self.rebuild()

    def _compose_answer(self, citations: list[RetrievedChunk]) -> str:
        best = citations[0].text
        lines = [line.strip("- ").strip() for line in best.splitlines() if line.strip()]
        policy_lines = [line for line in lines if not line.startswith("#")]
        selected = policy_lines[:5]
        return " ".join(selected)
