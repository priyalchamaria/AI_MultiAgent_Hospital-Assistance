from __future__ import annotations

import re


FORBIDDEN_KEYWORDS = [
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "TRUNCATE",
    "PRAGMA",
    "ATTACH",
    "DETACH",
    "REPLACE",
    "CREATE",
]


class SQLValidationError(ValueError):
    pass


class SQLValidator:
    def __init__(self, allowed_columns: set[str], max_rows: int = 100) -> None:
        self.allowed_columns = allowed_columns
        self.max_rows = max_rows

    def validate_sql(self, sql: str) -> bool:
        normalized = re.sub(r"\s+", " ", sql.strip(), flags=re.MULTILINE)
        upper = normalized.upper()
        if not upper.startswith("SELECT"):
            raise SQLValidationError("Only SELECT queries are allowed.")
        for keyword in FORBIDDEN_KEYWORDS:
            if re.search(rf"\b{keyword}\b", upper):
                raise SQLValidationError(f"Blocked unsafe SQL keyword: {keyword}.")
        if ";" in normalized[:-1]:
            raise SQLValidationError("Multiple SQL statements are not allowed.")
        if "--" in normalized or "/*" in normalized or "*/" in normalized:
            raise SQLValidationError("SQL comments are not allowed.")
        return True

    def enforce_limit(self, sql: str) -> str:
        if re.search(r"\bLIMIT\b", sql, flags=re.IGNORECASE):
            return sql
        return f"{sql.rstrip(';')} LIMIT {self.max_rows}"
