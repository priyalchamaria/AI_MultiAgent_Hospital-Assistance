from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from src.config import QUERY_LOG_PATH


class QueryLogger:
    def __init__(self, path: Path = QUERY_LOG_PATH) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def log(self, response: dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": response.get("query"),
            "route": response.get("selected_agent"),
            "confidence": response.get("confidence"),
            "response_time": response.get("response_time"),
            "status": response.get("status"),
        }
        logs = self.read_logs()
        logs.append(entry)
        self.path.write_text(json.dumps(logs[-500:], indent=2), encoding="utf-8")

    def read_logs(self) -> list[dict[str, Any]]:
        if not self.path.exists():
            return []
        try:
            return json.loads(self.path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return []
