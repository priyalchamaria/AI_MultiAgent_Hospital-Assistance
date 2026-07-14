from __future__ import annotations

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agents.orchestrator_agent import OrchestratorAgent
from src.config import DB_PATH


def main() -> None:
    if not DB_PATH.exists():
        raise FileNotFoundError("Database not found. Run scripts/prepare_data.py first.")

    orchestrator = OrchestratorAgent()

    sql_query = "Show the top 5 hospitals with the most cancer patients."
    sql_route = orchestrator.classify_query(sql_query)
    assert sql_route["route"] == "sql", sql_route
    sql_result = orchestrator.process_query(sql_query, [])
    assert sql_result["table"]
    assert "GROUP BY hospital" in sql_result["sql_query"]

    rag_query = "When should abnormal test results be escalated?"
    rag_route = orchestrator.classify_query(rag_query)
    assert rag_route["route"] == "rag", rag_route
    rag_result = orchestrator.process_query(rag_query, [])
    assert rag_result["sources"]

    print("Smoke test passed.")
    print(f"SQL route: {sql_route['reason']}")
    print(f"SQL answer: {sql_result['answer']}")
    print(f"RAG route: {rag_route['reason']}")
    print(f"RAG answer: {rag_result['answer'][:180]}...")


if __name__ == "__main__":
    main()
