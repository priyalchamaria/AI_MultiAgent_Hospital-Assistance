from __future__ import annotations

import shutil
import sqlite3
import zipfile
from pathlib import Path

import pandas as pd

from database.schema import INDEX_SQL, PATIENT_SCHEMA_SQL
from src.config import DB_PATH, RAW_CSV_PATH


RENAME_MAP = {
    "Name": "name",
    "Age": "age",
    "Gender": "gender",
    "Blood Type": "blood_type",
    "Medical Condition": "medical_condition",
    "Date of Admission": "admission_date",
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


def extract_csv_from_archive(archive_path: Path, destination: Path = RAW_CSV_PATH) -> Path:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive_path) as archive:
        csv_names = [name for name in archive.namelist() if name.lower().endswith(".csv")]
        if not csv_names:
            raise FileNotFoundError("No CSV file found in archive.")
        with archive.open(csv_names[0]) as source, destination.open("wb") as target:
            shutil.copyfileobj(source, target)
    return destination


def clean_patient_data(csv_path: Path) -> tuple[pd.DataFrame, dict[str, int]]:
    df = pd.read_csv(csv_path)
    before_rows = len(df)
    df = df.rename(columns=RENAME_MAP)
    df = df.drop_duplicates()
    missing_values = int(df.isna().sum().sum())
    df = df.dropna(subset=["name", "age", "gender", "medical_condition", "admission_date"])

    df["admission_date"] = pd.to_datetime(df["admission_date"], errors="coerce")
    df["discharge_date"] = pd.to_datetime(df["discharge_date"], errors="coerce")
    df["age"] = pd.to_numeric(df["age"], errors="coerce").fillna(0).astype(int)
    df["billing_amount"] = pd.to_numeric(df["billing_amount"], errors="coerce").fillna(0).round(2)
    df["room_number"] = pd.to_numeric(df["room_number"], errors="coerce").fillna(0).astype(int)
    df["length_of_stay"] = (df["discharge_date"] - df["admission_date"]).dt.days.clip(lower=0).fillna(0).astype(int)
    df["admission_date"] = df["admission_date"].dt.strftime("%Y-%m-%d")
    df["discharge_date"] = df["discharge_date"].dt.strftime("%Y-%m-%d")
    df = df.dropna(subset=["admission_date"])
    df.insert(0, "patient_id", range(1, len(df) + 1))

    stats = {
        "source_rows": before_rows,
        "clean_rows": len(df),
        "duplicates_removed": before_rows - len(df),
        "missing_values_detected": missing_values,
    }
    return df, stats


def create_database(csv_path: Path = RAW_CSV_PATH, db_path: Path = DB_PATH) -> dict[str, int]:
    db_path.parent.mkdir(parents=True, exist_ok=True)
    df, stats = clean_patient_data(csv_path)
    with sqlite3.connect(db_path) as conn:
        conn.execute("DROP TABLE IF EXISTS patients")
        conn.execute(PATIENT_SCHEMA_SQL)
        df.to_sql("patients", conn, if_exists="append", index=False)
        for sql in INDEX_SQL:
            conn.execute(sql)
    stats["columns"] = len(df.columns)
    return stats
