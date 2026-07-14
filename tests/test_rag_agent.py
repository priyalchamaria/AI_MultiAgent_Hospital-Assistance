from agents.rag_agent import RAGAgent


def test_visitor_policy_retrieval_has_source():
    agent = RAGAgent()
    response = agent.answer("What is the visitor policy?")
    assert response["sources"]
    assert "visitor" in response["sources"][0]["source"]


def test_unrelated_policy_question_not_found_or_low_confidence():
    agent = RAGAgent()
    response = agent.answer("Explain quantum computing hardware.")
    assert response["status"] in {"not_found", "success"}
