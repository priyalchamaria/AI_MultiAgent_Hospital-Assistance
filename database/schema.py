PATIENT_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS patients (
    patient_id INTEGER PRIMARY KEY,
    name TEXT,
    age INTEGER,
    gender TEXT,
    blood_type TEXT,
    medical_condition TEXT,
    admission_date TEXT,
    doctor TEXT,
    hospital TEXT,
    insurance_provider TEXT,
    billing_amount REAL,
    room_number INTEGER,
    admission_type TEXT,
    discharge_date TEXT,
    medication TEXT,
    test_results TEXT,
    length_of_stay INTEGER
);
"""

INDEX_SQL = [
    "CREATE INDEX IF NOT EXISTS idx_condition ON patients(medical_condition);",
    "CREATE INDEX IF NOT EXISTS idx_doctor ON patients(doctor);",
    "CREATE INDEX IF NOT EXISTS idx_hospital ON patients(hospital);",
    "CREATE INDEX IF NOT EXISTS idx_admission_date ON patients(admission_date);",
    "CREATE INDEX IF NOT EXISTS idx_admission_type ON patients(admission_type);",
    "CREATE INDEX IF NOT EXISTS idx_test_results ON patients(test_results);",
]

PATIENT_COLUMNS = {
    "patient_id",
    "name",
    "age",
    "gender",
    "blood_type",
    "medical_condition",
    "admission_date",
    "doctor",
    "hospital",
    "insurance_provider",
    "billing_amount",
    "room_number",
    "admission_type",
    "discharge_date",
    "medication",
    "test_results",
    "length_of_stay",
}
