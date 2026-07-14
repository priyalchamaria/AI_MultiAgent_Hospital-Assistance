from __future__ import annotations

import json
import sys
import time
from collections import Counter
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agents.orchestrator_agent import OrchestratorAgent


def main() -> None:
    test_path = Path(__file__).with_name("test_queries.json")
    queries = json.loads(test_path.read_text(encoding="utf-8"))
    orchestrator = OrchestratorAgent()
    rows = []
    route_counts = Counter()
    success_count = 0
    unsafe_blocked = 0
    latencies = []

    for item in queries:
        start = time.perf_counter()
        decision = orchestrator.classify_query(item["query"])
        response = orchestrator.process_query(item["query"], [])
        latency = time.perf_counter() - start
        latencies.append(latency)
        actual = decision["route"]
        expected = item["expected_route"]
        route_counts[actual] += 1
        correct = actual == expected
        success_count += int(correct)
        if "DROP" in item["query"].upper() and response["status"] in {"unsupported", "blocked"}:
            unsafe_blocked += 1
        rows.append(
            {
                "query": item["query"],
                "expected_route": expected,
                "actual_route": actual,
                "correct": correct,
                "status": response["status"],
                "latency": round(latency, 3),
            }
        )

    total = len(queries)
    results = {
        "routing_accuracy": round(success_count / total, 3),
        "end_to_end_success_rate": round(sum(row["status"] == "success" for row in rows) / total, 3),
        "unsafe_query_blocking_rate": unsafe_blocked,
        "average_latency": round(sum(latencies) / total, 3),
        "agent_usage_distribution": dict(route_counts),
        "confusion_rows": rows,
    }
    output = Path(__file__).with_name("results.json")
    output.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
