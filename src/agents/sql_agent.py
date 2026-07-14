from __future__ import annotations

import re
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from src.config import DB_PATH, PATIENT_TABLE
from src.text_utils import normalize_text


@dataclass
class SQLAgentResult:
    answer: str
    sql: str
    dataframe: pd.DataFrame
    explanation: str


class NLPToSQLAgent:
    """Rule-guided natural-language to SQL agent for the synthetic patient database."""

    dimensions = {
        "hospital": "hospital",
        "insurance": "insurance_provider",
        "insurance provider": "insurance_provider",
        "medical condition": "medical_condition",
        "condition": "medical_condition",
        "admission type": "admission_type",
        "gender": "gender",
        "blood type": "blood_type",
        "medication": "medication",
        "test result": "test_results",
        "test results": "test_results",
        "doctor": "doctor",
    }

    filters = {
        "emergency": ("admission_type", "Emergency"),
        "urgent": ("admission_type", "Urgent"),
        "elective": ("admission_type", "Elective"),
        "abnormal": ("test_results", "Abnormal"),
        "normal": ("test_results", "Normal"),
        "inconclusive": ("test_results", "Inconclusive"),
        "cancer": ("medical_condition", "Cancer"),
        "diabetes": ("medical_condition", "Diabetes"),
        "obesity": ("medical_condition", "Obesity"),
        "asthma": ("medical_condition", "Asthma"),
        "hypertension": ("medical_condition", "Hypertension"),
        "arthritis": ("medical_condition", "Arthritis"),
    }

    def __init__(self, db_path: Path = DB_PATH) -> None:
        self.db_path = db_path

    def answer(self, query: str) -> SQLAgentResult:
        sql, params, explanation = self._build_sql(query)
        with sqlite3.connect(self.db_path) as conn:
            dataframe = pd.read_sql_query(sql, conn, params=params)
        answer = self._format_answer(query, dataframe)
        return SQLAgentResult(answer=answer, sql=self._render_sql(sql, params), dataframe=dataframe, explanation=explanation)

    def _build_sql(self, query: str) -> tuple[str, list[str], str]:
        normalized = normalize_text(query)
        limit = self._extract_limit(normalized)
        group_by = self._extract_dimension(normalized)
        metric_expr, metric_alias, metric_label = self._extract_metric(normalized)
        where_sql, params = self._extract_filters(normalized)

        if group_by:
            sql = (
                f"SELECT {group_by}, {metric_expr} AS {metric_alias} "
                f"FROM {PATIENT_TABLE} {where_sql} "
                f"GROUP BY {group_by} "
                f"ORDER BY {metric_alias} DESC "
                f"LIMIT {limit}"
            )
            explanation = f"Grouped patient records by {group_by} and calculated {metric_label}."
        else:
            sql = f"SELECT {metric_expr} AS {metric_alias} FROM {PATIENT_TABLE} {where_sql}"
            explanation = f"Calculated {metric_label} across matching patient records."
        return sql, params, explanation

    def _extract_metric(self, normalized: str) -> tuple[str, str, str]:
        if any(term in normalized for term in ["average billing", "avg billing", "mean billing"]):
            return "ROUND(AVG(billing_amount), 2)", "average_billing_amount", "average billing amount"
        if any(term in normalized for term in ["total billing", "sum billing", "revenue"]):
            return "ROUND(SUM(billing_amount), 2)", "total_billing_amount", "total billing amount"
        if "average age" in normalized or "avg age" in normalized:
            return "ROUND(AVG(age), 1)", "average_age", "average age"
        if "average stay" in normalized or "length of stay" in normalized:
            return "ROUND(AVG(length_of_stay), 1)", "average_length_of_stay", "average length of stay"
        return "COUNT(*)", "record_count", "record count"

    def _extract_dimension(self, normalized: str) -> str | None:
        for phrase, column in sorted(self.dimensions.items(), key=lambda item: len(item[0]), reverse=True):
            if f" by {phrase}" in normalized or f" per {phrase}" in normalized:
                return column
        for phrase, column in sorted(self.dimensions.items(), key=lambda item: len(item[0]), reverse=True):
            if phrase in normalized and any(term in normalized for term in ["top", "most", "highest", "breakdown"]):
                return column
        return None

    def _extract_filters(self, normalized: str) -> tuple[str, list[str]]:
        clauses: list[str] = []
        params: list[str] = []
        for keyword, (column, value) in self.filters.items():
            if keyword in normalized:
                clauses.append(f"{column} = ?")
                params.append(value)

        year_match = re.search(r"\b(20\d{2})\b", normalized)
        if year_match:
            clauses.append("strftime('%Y', date_of_admission) = ?")
            params.append(year_match.group(1))

        if not clauses:
            return "", params
        return "WHERE " + " AND ".join(clauses), params

    def _extract_limit(self, normalized: str) -> int:
        match = re.search(r"\btop\s+(\d{1,2})\b", normalized)
        if match:
            return max(1, min(int(match.group(1)), 25))
        return 10

    def _format_answer(self, query: str, dataframe: pd.DataFrame) -> str:
        if dataframe.empty:
            return "No matching patient records were found."
        if dataframe.shape == (1, 1):
            column = dataframe.columns[0]
            value = dataframe.iloc[0, 0]
            return f"The {column.replace('_', ' ')} is {value}."
        top = dataframe.iloc[0].to_dict()
        pieces = [f"{key.replace('_', ' ')}: {value}" for key, value in top.items()]
        return "Top result: " + "; ".join(pieces) + "."

    def _render_sql(self, sql: str, params: list[str]) -> str:
        rendered = sql
        for param in params:
            rendered = rendered.replace("?", f"'{param}'", 1)
        return rendered
