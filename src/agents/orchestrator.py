from __future__ import annotations

from dataclasses import dataclass

from src.text_utils import normalize_text


@dataclass(frozen=True)
class RouteDecision:
    route: str
    confidence: float
    reason: str


class OrchestratorAgent:
    """Classifies plain-English questions and routes them to the right specialist."""

    structured_keywords = {
        "how many",
        "count",
        "average",
        "avg",
        "total",
        "sum",
        "highest",
        "lowest",
        "top",
        "by hospital",
        "by insurance",
        "by medical condition",
        "patients",
        "admissions",
        "billing",
        "age",
        "gender",
        "blood type",
        "test results",
        "medication",
        "doctor",
    }
    policy_keywords = {
        "policy",
        "procedure",
        "guideline",
        "rule",
        "privacy",
        "access control",
        "discharge planning",
        "escalate",
        "escalation",
        "medication reconciliation",
        "infection",
        "hand hygiene",
        "billing office",
        "documentation",
        "compliance",
    }

    def classify(self, query: str) -> RouteDecision:
        normalized = normalize_text(query)
        structured_score = sum(1 for keyword in self.structured_keywords if keyword in normalized)
        policy_score = sum(1 for keyword in self.policy_keywords if keyword in normalized)

        if policy_score > 0 and policy_score >= structured_score:
            confidence = min(0.95, 0.55 + 0.1 * policy_score)
            return RouteDecision(
                route="rag",
                confidence=confidence,
                reason=f"Policy intent detected from {policy_score} policy keyword match(es).",
            )
        if structured_score > 0:
            confidence = min(0.95, 0.55 + 0.08 * structured_score)
            return RouteDecision(
                route="sql",
                confidence=confidence,
                reason=f"Data-analysis intent detected from {structured_score} structured keyword match(es).",
            )
        return RouteDecision(
            route="rag",
            confidence=0.5,
            reason="No strong database aggregation signal found, so the safer default is document retrieval.",
        )
