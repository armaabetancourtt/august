from august.llm.grounded_agent import Document, GroundedAgent

def test_agent_cites_retrieved_sources():
    agent = GroundedAgent([Document("valuation", "Property valuation uses comparable sales.")])
    response = agent.answer("property valuation comparable sales")
    assert response["grounded"]
    assert response["citations"] == ["valuation"]

def test_agent_refuses_unsupported_claim():
    agent = GroundedAgent([Document("d1", "Residential valuations")])
    result = agent.answer("quantum photon satellite")
    assert result["grounded"] is False
    assert result["citations"] == []
