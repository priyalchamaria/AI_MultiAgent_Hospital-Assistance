from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

import pandas as pd

from src.config import DB_PATH


def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn


def execute_read_query(sql: str, params: tuple[Any, ...] = (), db_path: Path = DB_PATH) -> pd.DataFrame:
    with connect(db_path) as conn:
        conn.execute("PRAGMA query_only = ON")
        return pd.read_sql_query(sql, conn, params=params)
