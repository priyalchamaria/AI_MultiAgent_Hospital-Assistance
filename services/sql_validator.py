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
        self.allowed_tables = {"patients"}
        self.allowed_functions = {
            "avg",
            "count",
            "lower",
            "max",
            "min",
            "round",
            "strftime",
            "sum",
        }
        self.sql_keywords = {
            "and",
            "as",
            "asc",
            "by",
            "desc",
            "from",
            "group",
            "limit",
            "order",
            "select",
            "where",
        }

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
        if re.search(r"\bsqlite_master\b", normalized, flags=re.IGNORECASE):
            raise SQLValidationError("Access to SQLite system tables is not allowed.")
        if re.search(r"\(\s*SELECT\b", normalized, flags=re.IGNORECASE):
            raise SQLValidationError("Subqueries are not allowed in this demo SQL layer.")
        self._validate_tables(normalized)
        self._validate_identifiers(normalized)
        return True

    def enforce_limit(self, sql: str) -> str:
        match = re.search(r"\bLIMIT\s+(\d+)", sql, flags=re.IGNORECASE)
        if match:
            requested_limit = int(match.group(1))
            if requested_limit > self.max_rows:
                return re.sub(
                    r"\bLIMIT\s+\d+",
                    f"LIMIT {self.max_rows}",
                    sql,
                    flags=re.IGNORECASE,
                )
            return sql
        return f"{sql.rstrip(';')} LIMIT {self.max_rows}"

    def _validate_tables(self, sql: str) -> None:
        table_names = re.findall(r"\b(?:FROM|JOIN)\s+([A-Za-z_][A-Za-z0-9_]*)", sql, flags=re.IGNORECASE)
        if not table_names:
            raise SQLValidationError("A SELECT query must read from the patients table.")
        for table_name in table_names:
            if table_name.lower() not in self.allowed_tables:
                raise SQLValidationError(f"Table is not allowed: {table_name}.")

    def _validate_identifiers(self, sql: str) -> None:
        without_strings = re.sub(r"'[^']*'", " ", sql)
        aliases = {
            alias.lower()
            for alias in re.findall(r"\bAS\s+([A-Za-z_][A-Za-z0-9_]*)", without_strings, flags=re.IGNORECASE)
        }
        identifiers = {
            identifier.lower()
            for identifier in re.findall(r"\b[A-Za-z_][A-Za-z0-9_]*\b", without_strings)
        }
        allowed = (
            {column.lower() for column in self.allowed_columns}
            | self.allowed_tables
            | self.allowed_functions
            | self.sql_keywords
            | aliases
        )
        for identifier in sorted(identifiers - allowed):
            raise SQLValidationError(f"Column or identifier is not allowed: {identifier}.")
