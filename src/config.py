from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
POLICY_DIR = DATA_DIR / "policies"
LOG_DIR = BASE_DIR / "logs"
TEST_DB_PATH = DATA_DIR / "test_hospital.db"

RAW_CSV_PATH = DATA_DIR / "healthcare_dataset.csv"
DB_PATH = DATA_DIR / "hospital.db"
RAG_INDEX_PATH = DATA_DIR / "policy_index.pkl"
QUERY_LOG_PATH = LOG_DIR / "query_logs.json"

PATIENT_TABLE = "patients"

DISPLAY_COLUMNS = {
    "name": "Name",
    "patient_id": "Patient ID",
    "age": "Age",
    "gender": "Gender",
    "blood_type": "Blood Type",
    "medical_condition": "Medical Condition",
    "date_of_admission": "Date of Admission",
    "doctor": "Doctor",
    "hospital": "Hospital",
    "insurance_provider": "Insurance Provider",
    "billing_amount": "Billing Amount",
    "room_number": "Room Number",
    "admission_type": "Admission Type",
    "discharge_date": "Discharge Date",
    "medication": "Medication",
    "test_results": "Test Results",
    "length_of_stay": "Length of Stay",
}
