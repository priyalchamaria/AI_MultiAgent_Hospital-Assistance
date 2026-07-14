from __future__ import annotations

from sklearn.feature_extraction.text import TfidfVectorizer


class LocalTfidfEmbeddings:
    """Offline embedding model for evaluator-friendly local runs.

    The project architecture mirrors an embedding pipeline; TF-IDF is used so the
    app runs without downloading sentence-transformer weights.
    """

    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))

    def fit_transform(self, texts: list[str]):
        return self.vectorizer.fit_transform(texts)

    def transform(self, texts: list[str]):
        return self.vectorizer.transform(texts)
