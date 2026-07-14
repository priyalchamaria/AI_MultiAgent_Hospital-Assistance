import pytest

from agents.sql_agent import SQLAgent
from services.sql_validator import SQLValidationError, SQLValidator
from database.schema import PATIENT_COLUMNS


@pytest.mark.parametrize(
    "sql",
    [
        "DROP TABLE patients",
        "DELETE FROM patients",
        "UPDATE patients SET name = 'x'",
        "INSERT INTO patients(name) VALUES ('x')",
        "PRAGMA table_info(patients)",
        "SELECT * FROM patients; DROP TABLE patients;",
    ],
)
def test_dangerous_sql_is_blocked(sql):
    validator = SQLValidator(PATIENT_COLUMNS)
    with pytest.raises(SQLValidationError):
        validator.validate_sql(sql)


def test_prompted_delete_request_is_not_executed():
    agent = SQLAgent()
    response = agent.answer("Delete all patient records")
    assert response["status"] in {"blocked", "success"}
    assert "DELETE" not in str(response.get("sql_query", "")).upper()
