import pytest
from app.agents.rag_agent import rag_agent
from app.agents.state import AgentState
from app.vector_store.qdrant_client import qdrant_store

@pytest.mark.asyncio
async def test_qdrant_indexing_and_search():
    doc_id = await qdrant_store.add_document(
        title="Test Return Guidelines",
        content="Items can be returned within 45 days with original proof of purchase.",
        category="Test Category"
    )
    assert doc_id is not None

    hits = await qdrant_store.search_similar("Test Return Guidelines", limit=2, score_threshold=0.0)
    assert len(hits) > 0
    assert "Test Return Guidelines" in hits[0]["title"]

@pytest.mark.asyncio
async def test_rag_agent_execution():
    state: AgentState = {
        "session_id": "test_sess_6",
        "user_message": "What is the return policy?",
        "history": [],
        "intent": "rag_query",
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
    output = await rag_agent.run(state)
    assert len(output["retrieved_docs"]) > 0
    assert len(output["raw_answer"]) > 10
    assert "RAGAgent" in output["agent_trajectory"]
