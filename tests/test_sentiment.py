import pytest
from app.agents.sentiment_agent import sentiment_agent
from app.agents.state import AgentState

@pytest.mark.asyncio
async def test_sentiment_positive():
    state: AgentState = {
        "session_id": "test_sess_4",
        "user_message": "Thank you so much! That was very helpful and awesome.",
        "history": [],
        "intent": "general_inquiry",
        "sentiment_label": "neutral",
        "sentiment_score": 0.5,
        "retrieved_docs": [],
        "raw_answer": "",
        "escalation_required": False,
        "ticket_id": None,
        "ticket_number": None,
        "ticket_summary": None,
        "final_response": "",
        "agent_trajectory": [],
        "confidence_score": 0.5
    }
    output = await sentiment_agent.run(state)
    assert output["sentiment_label"] == "positive"
    assert output["sentiment_score"] > 0.6
    assert output["escalation_required"] is False
    assert "SentimentAgent" in output["agent_trajectory"]

@pytest.mark.asyncio
async def test_sentiment_frustration_escalation():
    state: AgentState = {
        "session_id": "test_sess_5",
        "user_message": "This is ridiculous! My item is completely broken and your service is terrible. Give my money back!",
        "history": [],
        "intent": "complaint",
        "sentiment_label": "neutral",
        "sentiment_score": 0.5,
        "retrieved_docs": [],
        "raw_answer": "",
        "escalation_required": False,
        "ticket_id": None,
        "ticket_number": None,
        "ticket_summary": None,
        "final_response": "",
        "agent_trajectory": [],
        "confidence_score": 0.5
    }
    output = await sentiment_agent.run(state)
    assert output["sentiment_label"] in ["frustrated", "angry"]
    assert output["sentiment_score"] <= 0.35
    assert output["escalation_required"] is True
