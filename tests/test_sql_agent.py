from agents.sql_agent import SQLAgent


def test_count_sql_generation():
    agent = SQLAgent()
    sql, params = agent.generate_sql("How many female patients have diabetes?")
    assert "COUNT" in sql
    assert "gender" in sql
    assert "medical_condition" in sql
    assert params


def test_average_group_by_generation():
    agent = SQLAgent()
    sql, _ = agent.generate_sql("What is the average billing amount by insurance provider?")
    assert "AVG(billing_amount)" in sql
    assert "GROUP BY insurance_provider" in sql


def test_top_n_generation():
    agent = SQLAgent()
    sql, _ = agent.generate_sql("Show the top 5 hospitals with the most cancer patients.")
    assert "GROUP BY hospital" in sql
    assert "LIMIT 5" in sql


def test_sql_agent_executes_count():
    agent = SQLAgent()
    response = agent.answer("How many patients are there?")
    assert response["status"] == "success"
    assert response["table"]
