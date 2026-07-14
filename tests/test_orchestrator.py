from agents.orchestrator_agent import OrchestratorAgent


def test_sql_query_routes_to_sql():
    agent = OrchestratorAgent()
    decision = agent.classify_query("How many female patients have diabetes?")
    assert decision["route"] == "sql"


def test_policy_query_routes_to_rag():
    agent = OrchestratorAgent()
    decision = agent.classify_query("What is the visitor policy?")
    assert decision["route"] == "rag"


def test_mixed_query_routes_to_both():
    agent = OrchestratorAgent()
    decision = agent.classify_query("How many diabetic patients are there and what is the discharge policy?")
    assert decision["route"] == "both"


def test_unsupported_query_rejected():
    agent = OrchestratorAgent()
    decision = agent.classify_query("What is the weather today?")
    assert decision["route"] == "unsupported"
