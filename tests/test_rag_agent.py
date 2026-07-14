from agents.rag_agent import RAGAgent


def test_visitor_policy_retrieval_has_source():
    agent = RAGAgent()
    response = agent.answer("What is the visitor policy?")
    assert response["status"] == "success"
    assert response["sources"]
    assert "visitor" in response["sources"][0]["source"]
    assert response["sources"][0]["section"] == "Procedure"
    assert "10:00 AM to 7:00 PM" in response["answer"]


def test_visiting_hours_paraphrase_returns_correct_section():
    agent = RAGAgent()
    response = agent.answer("What are the visiting hours?")
    assert response["status"] == "success"
    assert response["sources"][0]["source"] == "visitor_policy.txt"
    assert response["sources"][0]["section"] == "Procedure"
    assert "10:00 AM to 7:00 PM" in response["answer"]


def test_unrelated_policy_question_not_found():
    agent = RAGAgent()
    response = agent.answer("Explain quantum computing hardware.")
    assert response["status"] == "not_found"
    assert response["sources"] == []
