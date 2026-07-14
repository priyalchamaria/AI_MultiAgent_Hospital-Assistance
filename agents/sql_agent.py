from __future__ import annotations

import re
import sqlite3
import time
from pathlib import Path
from typing import Any

import pandas as pd

from database.db_utils import execute_read_query
from database.schema import PATIENT_COLUMNS
from services.response_formatter import unified_response
from services.sql_validator import SQLValidationError, SQLValidator
from src.config import DB_PATH
from src.text_utils import normalize_text


class SQLAgent:
    dimensions = {
        "hospital": "hospital",
        "doctor": "doctor",
        "insurance": "insurance_provider",
        "insurance provider": "insurance_provider",
        "condition": "medical_condition",
        "medical condition": "medical_condition",
        "gender": "gender",
        "admission type": "admission_type",
        "medication": "medication",
        "test result": "test_results",
        "blood type": "blood_type",
    }
    filters = {
        "female": ("gender", "Female"),
        "male": ("gender", "Male"),
        "emergency": ("admission_type", "Emergency"),
        "urgent": ("admission_type", "Urgent"),
        "elective": ("admission_type", "Elective"),
        "abnormal": ("test_results", "Abnormal"),
        "normal": ("test_results", "Normal"),
        "inconclusive": ("test_results", "Inconclusive"),
        "diabetes": ("medical_condition", "Diabetes"),
        "cancer": ("medical_condition", "Cancer"),
        "obesity": ("medical_condition", "Obesity"),
        "asthma": ("medical_condition", "Asthma"),
        "hypertension": ("medical_condition", "Hypertension"),
        "arthritis": ("medical_condition", "Arthritis"),
    }

    def __init__(self, db_path: Path = DB_PATH, max_rows: int = 100) -> None:
        self.db_path = db_path
        self.max_rows = max_rows
        self.validator = SQLValidator(PATIENT_COLUMNS, max_rows=max_rows)

    def generate_sql(self, query: str, memory_filters: dict[str, str] | None = None) -> tuple[str, tuple[Any, ...]]:
        normalized = normalize_text(query)
        metric, alias = self._metric(normalized)
        group_by = self._group_by(normalized)
        filters = self._filters(normalized)
        if memory_filters and any(word in normalized for word in ["them", "those", "these patients"]):
            filters.update(memory_filters)
        params = tuple(filters.values())
        where = " AND ".join([f"LOWER({column}) = LOWER(?)" for column in filters])
        where_sql = f" WHERE {where}" if where else ""

        if self._is_lookup(normalized):
            sql = (
                "SELECT patient_id, name, age, gender, medical_condition, admission_date, doctor, hospital, "
                "insurance_provider, billing_amount, medication, test_results FROM patients"
                f"{where_sql} ORDER BY admission_date DESC"
            )
            return self.validator.enforce_limit(sql), params

        if group_by:
            limit = self._limit(normalized)
            sql = (
                f"SELECT {group_by}, {metric} AS {alias} FROM patients{where_sql} "
                f"GROUP BY {group_by} ORDER BY {alias} DESC LIMIT {limit}"
            )
            return sql, params
        sql = f"SELECT {metric} AS {alias} FROM patients{where_sql}"
        return sql, params

    def validate_sql(self, sql: str) -> bool:
        return self.validator.validate_sql(sql)

    def execute_sql(self, sql: str, params: tuple[Any, ...] = ()) -> pd.DataFrame:
        self.validate_sql(sql)
        sql = self.validator.enforce_limit(sql)
        return execute_read_query(sql, params=params, db_path=self.db_path)

    def format_result(self, query: str, result: pd.DataFrame) -> str:
        if result.empty:
            return "No matching patient records were found."
        if result.shape == (1, 1):
            label = result.columns[0].replace("_", " ")
            value = result.iloc[0, 0]
            return f"The {label} is {value}."
        first = result.iloc[0].to_dict()
        return "Top result: " + "; ".join(f"{key.replace('_', ' ')}: {value}" for key, value in first.items()) + "."

    def answer(
        self,
        query: str,
        *,
        confidence: float = 0.9,
        route_reason: str = "",
        memory_filters: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        start = time.perf_counter()
        try:
            sql, params = self.generate_sql(query, memory_filters=memory_filters)
            df = self.execute_sql(sql, params)
            answer = self.format_result(query, df)
            return unified_response(
                query=query,
                selected_agent="SQL Agent",
                answer=answer,
                sql_query=self._render_sql(sql, params),
                table=df.to_dict("records"),
                confidence=confidence,
                start_time=start,
                route_reason=route_reason,
            )
        except (SQLValidationError, sqlite3.Error, pd.errors.DatabaseError) as exc:
            return unified_response(
                query=query,
                selected_agent="SQL Agent",
                answer=f"The SQL request could not be completed safely: {exc}",
                confidence=confidence,
                start_time=start,
                status="blocked",
                route_reason=route_reason,
            )

    def extract_memory_filters(self, query: str) -> dict[str, str]:
        return self._filters(normalize_text(query))

    def _metric(self, normalized: str) -> tuple[str, str]:
        if "average age" in normalized:
            return "ROUND(AVG(age), 1)", "average_age"
        if "average" in normalized and "billing" in normalized:
            return "ROUND(AVG(billing_amount), 2)", "average_billing_amount"
        if "minimum" in normalized or "lowest" in normalized:
            target = "billing_amount" if "billing" in normalized else "age"
            return f"MIN({target})", f"minimum_{target}"
        if "maximum" in normalized or "highest" in normalized or "max" in normalized:
            target = "billing_amount" if "billing" in normalized else "age"
            return f"MAX({target})", f"maximum_{target}"
        if "total" in normalized and "billing" in normalized:
            return "ROUND(SUM(billing_amount), 2)", "total_billing_amount"
        if "length of stay" in normalized or "average stay" in normalized:
            return "ROUND(AVG(length_of_stay), 1)", "average_length_of_stay"
        return "COUNT(*)", "record_count"

    def _group_by(self, normalized: str) -> str | None:
        for phrase, column in sorted(self.dimensions.items(), key=lambda item: len(item[0]), reverse=True):
            if f" by {phrase}" in normalized or f" per {phrase}" in normalized:
                return column
        for phrase, column in self.dimensions.items():
            if phrase in normalized and any(word in normalized for word in ["top", "most", "breakdown"]):
                return column
        return None

    def _filters(self, normalized: str) -> dict[str, str]:
        found: dict[str, str] = {}
        for keyword, (column, value) in self.filters.items():
            if self._keyword_matches(normalized, keyword):
                found[column] = value
        year = re.search(r"\b(20\d{2})\b", normalized)
        if year:
            found["strftime('%Y', admission_date)"] = year.group(1)
        return found

    def _keyword_matches(self, normalized: str, keyword: str) -> bool:
        if " " in keyword:
            return keyword in normalized
        return re.search(rf"\b{re.escape(keyword)}\b", normalized) is not None

    def _limit(self, normalized: str) -> int:
        match = re.search(r"\btop\s+(\d{1,2})\b", normalized)
        return max(1, min(int(match.group(1)), self.max_rows)) if match else 10

    def _is_lookup(self, normalized: str) -> bool:
        return any(term in normalized for term in ["list patients", "show patients", "patient lookup", "show me patients"])

    def _render_sql(self, sql: str, params: tuple[Any, ...]) -> str:
        rendered = sql
        for param in params:
            rendered = rendered.replace("?", f"'{param}'", 1)
        return rendered
