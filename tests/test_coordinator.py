import pytest
from app.agents.coordinator_agent import coordinator_agent
from app.agents.state import AgentState

@pytest.mark.asyncio
async def test_coordinator_greeting():
    initial_state: AgentState = {
        "session_id": "test_sess_1",
        "user_message": "Hello",
        "history": [],
        "intent": "",
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
    output = await coordinator_agent.run(initial_state)
    assert output["intent"] == "greeting"
    assert "CoordinatorAgent" in output["agent_trajectory"]

@pytest.mark.asyncio
async def test_coordinator_escalation_intent():
    initial_state: AgentState = {
        "session_id": "test_sess_2",
        "user_message": "I want to speak with a human manager right now",
        "history": [],
        "intent": "",
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
    output = await coordinator_agent.run(initial_state)
    assert output["intent"] == "escalation_request"

@pytest.mark.asyncio
async def test_coordinator_rag_query():
    initial_state: AgentState = {
        "session_id": "test_sess_3",
        "user_message": "What is the return policy for electronics?",
        "history": [],
        "intent": "",
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
    output = await coordinator_agent.run(initial_state)
    assert output["intent"] == "rag_query"
