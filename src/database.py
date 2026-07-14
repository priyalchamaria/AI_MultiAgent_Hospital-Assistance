from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

from src.config import DB_PATH, PATIENT_TABLE


RENAME_MAP = {
    "Name": "name",
    "Age": "age",
    "Gender": "gender",
    "Blood Type": "blood_type",
    "Medical Condition": "medical_condition",
    "Date of Admission": "date_of_admission",
    "Doctor": "doctor",
    "Hospital": "hospital",
    "Insurance Provider": "insurance_provider",
    "Billing Amount": "billing_amount",
    "Room Number": "room_number",
    "Admission Type": "admission_type",
    "Discharge Date": "discharge_date",
    "Medication": "medication",
    "Test Results": "test_results",
}


def normalize_patient_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    normalized = df.rename(columns=RENAME_MAP).copy()
    normalized["date_of_admission"] = pd.to_datetime(normalized["date_of_admission"], errors="coerce")
    normalized["discharge_date"] = pd.to_datetime(normalized["discharge_date"], errors="coerce")
    normalized["length_of_stay"] = (
        normalized["discharge_date"] - normalized["date_of_admission"]
    ).dt.days.clip(lower=0)
    normalized["billing_amount"] = pd.to_numeric(normalized["billing_amount"], errors="coerce").round(2)
    normalized["age"] = pd.to_numeric(normalized["age"], errors="coerce").astype("Int64")
    normalized["room_number"] = pd.to_numeric(normalized["room_number"], errors="coerce").astype("Int64")
    normalized.insert(0, "record_id", range(1, len(normalized) + 1))
    normalized["date_of_admission"] = normalized["date_of_admission"].dt.strftime("%Y-%m-%d")
    normalized["discharge_date"] = normalized["discharge_date"].dt.strftime("%Y-%m-%d")
    return normalized


def build_patient_database(csv_path: Path, db_path: Path = DB_PATH) -> dict[str, int]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(csv_path)
    normalized = normalize_patient_dataframe(df)
    with sqlite3.connect(db_path) as conn:
        normalized.to_sql(PATIENT_TABLE, conn, if_exists="replace", index=False)
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{PATIENT_TABLE}_condition ON {PATIENT_TABLE}(medical_condition)")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{PATIENT_TABLE}_admission_type ON {PATIENT_TABLE}(admission_type)")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{PATIENT_TABLE}_test_results ON {PATIENT_TABLE}(test_results)")
        conn.execute(f"CREATE INDEX IF NOT EXISTS idx_{PATIENT_TABLE}_hospital ON {PATIENT_TABLE}(hospital)")
    return {"rows": len(normalized), "columns": len(normalized.columns)}


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn
