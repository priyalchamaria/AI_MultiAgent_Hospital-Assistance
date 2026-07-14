from __future__ import annotations

import pickle
from pathlib import Path

from sklearn.metrics.pairwise import cosine_similarity

from rag.embeddings import LocalTfidfEmbeddings
from src.config import RAG_INDEX_PATH


class LocalVectorStore:
    def __init__(self, index_path: Path = RAG_INDEX_PATH) -> None:
        self.index_path = index_path
        self.embedding_model = LocalTfidfEmbeddings()
        self.matrix = None
        self.metadata: list[dict[str, str]] = []

    def build(self, texts: list[str], metadata: list[dict[str, str]]) -> None:
        self.metadata = metadata
        self.matrix = self.embedding_model.fit_transform(texts)
        self.index_path.parent.mkdir(parents=True, exist_ok=True)
        with self.index_path.open("wb") as file:
            pickle.dump(
                {
                    "vectorizer": self.embedding_model.vectorizer,
                    "matrix": self.matrix,
                    "metadata": self.metadata,
                },
                file,
            )

    def load(self) -> bool:
        if not self.index_path.exists():
            return False
        with self.index_path.open("rb") as file:
            payload = pickle.load(file)
        self.embedding_model.vectorizer = payload["vectorizer"]
        self.matrix = payload["matrix"]
        self.metadata = payload["metadata"]
        return True

    def search(self, query: str, top_k: int = 3) -> list[dict[str, str | float]]:
        if self.matrix is None:
            return []
        query_vector = self.embedding_model.transform([query])
        scores = cosine_similarity(query_vector, self.matrix).flatten()
        indexes = scores.argsort()[::-1][:top_k]
        results = []
        for index in indexes:
            if scores[index] <= 0:
                continue
            item = dict(self.metadata[index])
            item["score"] = round(float(scores[index]), 3)
            results.append(item)
        return results
