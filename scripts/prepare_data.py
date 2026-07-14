from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from agents.rag_agent import RAGAgent
from database.create_database import create_database, extract_csv_from_archive
from src.config import POLICY_DIR, RAW_CSV_PATH
from src.policy_generator import ensure_policy_documents


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare CareBridge AI dataset and policy documents.")
    parser.add_argument("--archive", type=Path, help="Path to archive containing healthcare_dataset.csv")
    parser.add_argument("--csv", type=Path, help="Path to an already extracted healthcare CSV")
    args = parser.parse_args()

    if args.archive:
        csv_path = extract_csv_from_archive(args.archive, RAW_CSV_PATH)
    elif args.csv:
        RAW_CSV_PATH.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(args.csv, RAW_CSV_PATH)
        csv_path = RAW_CSV_PATH
    elif RAW_CSV_PATH.exists():
        csv_path = RAW_CSV_PATH
    else:
        raise FileNotFoundError("Provide --archive, --csv, or place healthcare_dataset.csv in data/raw/.")

    stats = create_database(csv_path)
    policies = ensure_policy_documents(POLICY_DIR)
    RAGAgent().build_index()
    print(f"Prepared SQLite database with {stats['clean_rows']:,} rows and {stats['columns']} columns.")
    print(f"Duplicates removed: {stats['duplicates_removed']:,}. Missing values detected: {stats['missing_values_detected']:,}.")
    print(f"Generated {len(policies)} policy documents in {POLICY_DIR}.")


if __name__ == "__main__":
    main()
