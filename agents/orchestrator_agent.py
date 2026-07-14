from __future__ import annotations

import time
from typing import Any

from agents.rag_agent import RAGAgent
from agents.sql_agent import SQLAgent
from services.logger import QueryLogger
from services.query_classifier import HybridQueryClassifier
from services.response_formatter import unified_response


class OrchestratorAgent:
    def __init__(self) -> None:
        self.classifier = HybridQueryClassifier()
        self.sql_agent = SQLAgent()
        self.rag_agent = RAGAgent()
        self.logger = QueryLogger()

    def classify_query(self, query: str) -> dict[str, Any]:
        result = self.classifier.classify_query(query)
        return {"route": result.route, "confidence": result.confidence, "reason": result.reason}

    def route_query(self, query: str, conversation_history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        decision = self.classifier.classify_query(query)
        memory_filters = self._memory_filters(conversation_history or [])
        if decision.route == "sql":
            return self.sql_agent.answer(
                query,
                confidence=decision.confidence,
                route_reason=decision.reason,
                memory_filters=memory_filters,
            )
        if decision.route == "rag":
            return self.rag_agent.answer(query, confidence=decision.confidence, route_reason=decision.reason)
        if decision.route == "both":
            return self._answer_with_both(query, decision, memory_filters)
        start = time.perf_counter()
        return unified_response(
            query=query,
            selected_agent="Unsupported",
            answer="This question is outside the hospital assistant's supported scope. Please ask about synthetic patient records or hospital policies.",
            confidence=decision.confidence,
            start_time=start,
            status="unsupported",
            route_reason=decision.reason,
        )

    def process_query(self, query: str, conversation_history: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        response = self.route_query(query, conversation_history)
        self.logger.log(response)
        return response

    def _answer_with_both(self, query, decision, memory_filters):
        start = time.perf_counter()
        sql_response = self.sql_agent.answer(query, confidence=decision.confidence, route_reason=decision.reason, memory_filters=memory_filters)
        rag_response = self.rag_agent.answer(query, confidence=decision.confidence, route_reason=decision.reason)
        return unified_response(
            query=query,
            selected_agent="SQL Agent + RAG Agent",
            answer=f"**Patient Data**\n\n{sql_response['answer']}\n\n**Policy Guidance**\n\n{rag_response['answer']}",
            sql_query=sql_response.get("sql_query"),
            table=sql_response.get("table", []),
            sources=rag_response.get("sources", []),
            confidence=decision.confidence,
            start_time=start,
            route_reason=decision.reason,
        )

    def _memory_filters(self, history: list[dict[str, Any]]) -> dict[str, str]:
        for item in reversed(history[-4:]):
            if item.get("selected_agent") == "SQL Agent":
                return self.sql_agent.extract_memory_filters(str(item.get("query", "")))
        return {}
