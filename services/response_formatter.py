from __future__ import annotations

import time
from typing import Any


def unified_response(
    *,
    query: str,
    selected_agent: str,
    answer: str,
    confidence: float,
    start_time: float,
    status: str = "success",
    sql_query: str | None = None,
    sources: list[dict[str, Any]] | None = None,
    table: list[dict[str, Any]] | None = None,
    route_reason: str = "",
) -> dict[str, Any]:
    return {
        "query": query,
        "selected_agent": selected_agent,
        "answer": answer,
        "sql_query": sql_query,
        "sources": sources or [],
        "table": table or [],
        "confidence": round(confidence, 3),
        "response_time": round(time.perf_counter() - start_time, 3),
        "status": status,
        "route_reason": route_reason,
    }
