from __future__ import annotations

from dataclasses import dataclass

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from src.text_utils import normalize_text


@dataclass(frozen=True)
class Classification:
    route: str
    confidence: float
    reason: str


class HybridQueryClassifier:
    sql_examples = [
        "how many patients have diabetes",
        "average billing amount by hospital",
        "top doctors by patient count",
        "patients admitted in 2022",
        "list female patients with abnormal test results",
        "highest billing insurance provider",
    ]
    rag_examples = [
        "what is the visitor policy",
        "what are the visiting hours",
        "what are the visitor timings",
        "what should staff do for incident reporting",
        "privacy procedure for medical records",
        "infection control guideline",
        "emergency response policy",
        "medication administration rule",
    ]
    unsupported_examples = [
        "what is the weather today",
        "write a poem",
        "book me a flight",
        "stock market prediction",
    ]

    sql_keywords = {
        "how many",
        "count",
        "average",
        "minimum",
        "maximum",
        "highest",
        "lowest",
        "top",
        "list patients",
        "doctor",
        "hospital",
        "admitted",
        "billing",
        "medication",
        "test result",
        "female",
        "male",
    }
    rag_keywords = {
        "policy",
        "procedure",
        "rule",
        "guideline",
        "allowed",
        "visitor",
        "visiting",
        "visitors",
        "hours",
        "timing",
        "timings",
        "privacy",
        "reporting",
        "what should staff do",
        "escalation",
        "escalate",
        "escalated",
        "access",
        "infection",
    }
    unsupported_keywords = {
        "weather",
        "flight",
        "stock",
        "password",
        "diagnose me",
        "treatment for me",
        "drop table",
        "delete all",
        "update the database",
        "insert into",
        "alter table",
        "truncate",
        "show me all database passwords",
        "ignore previous instructions",
    }

    def __init__(self) -> None:
        self.labels = ["sql"] * len(self.sql_examples) + ["rag"] * len(self.rag_examples) + [
            "unsupported"
        ] * len(self.unsupported_examples)
        corpus = self.sql_examples + self.rag_examples + self.unsupported_examples
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(corpus)

    def classify_query(self, query: str) -> Classification:
        normalized = normalize_text(query)
        if not normalized:
            return Classification("unsupported", 0.99, "Empty queries are outside the supported scope.")
        if len(normalized) > 600:
            return Classification("unsupported", 0.9, "The query is too long for the demo assistant.")
        if any(keyword in normalized for keyword in self.unsupported_keywords):
            return Classification("unsupported", 0.92, "The query is outside hospital records and policy scope.")

        sql_score = sum(1 for keyword in self.sql_keywords if keyword in normalized)
        rag_score = sum(1 for keyword in self.rag_keywords if keyword in normalized)
        if rag_score and any(word in normalized for word in ["escalate", "escalated", "escalation", "procedure", "policy"]):
            if any(word in normalized for word in ["how many", "count", "average", "top", "list patients"]):
                return Classification("both", 0.88, "The query combines patient data analysis with policy guidance.")
            return Classification("rag", 0.86, "Escalation or policy wording indicates a document-guidance question.")
        if sql_score and rag_score:
            return Classification("both", 0.88, "The query asks for both patient data and policy guidance.")

        vector = self.vectorizer.transform([query])
        similarities = cosine_similarity(vector, self.matrix).flatten()
        best_index = int(similarities.argmax())
        semantic_route = self.labels[best_index]
        semantic_score = float(similarities[best_index])

        if rag_score >= sql_score and rag_score > 0:
            return Classification("rag", min(0.96, 0.65 + rag_score * 0.07), "Policy keywords and semantic similarity indicate a document question.")
        if sql_score > 0:
            return Classification("sql", min(0.96, 0.65 + sql_score * 0.06), "Structured-data keywords indicate a patient database question.")
        if semantic_score < 0.08:
            return Classification("unsupported", 0.72, "No strong hospital-data or policy signal was found.")
        return Classification(semantic_route, min(0.9, 0.55 + semantic_score), "Semantic similarity selected the closest supported route.")
