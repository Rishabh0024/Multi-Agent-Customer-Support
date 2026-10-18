import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    response = await async_client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "components" in data

@pytest.mark.asyncio
async def test_chat_endpoint_normal_flow(async_client: AsyncClient):
    payload = {
        "session_id": "pytest_session_101",
        "message": "What are your shipping delivery times and costs?",
        "user_name": "Test Customer",
        "user_email": "customer@example.com"
    }
    response = await async_client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["session_id"] == "pytest_session_101"
    assert len(data["message"]) > 0
    assert "CoordinatorAgent" in data["agent_trajectory"]
    assert "RAGAgent" in data["agent_trajectory"]

@pytest.mark.asyncio
async def test_chat_endpoint_escalation_flow(async_client: AsyncClient):
    payload = {
        "session_id": "pytest_session_102",
        "message": "I demand to talk to a human manager immediately! Your product is broken!",
        "user_name": "Angry Customer",
        "user_email": "angry@example.com"
    }
    response = await async_client.post("/api/chat", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["escalation_required"] is True
    assert data["ticket_number"] is not None
    assert "TICK-" in data["ticket_number"]
    assert "EscalationAgent" in data["agent_trajectory"]

@pytest.mark.asyncio
async def test_tickets_list_and_stats(async_client: AsyncClient):
    stats_res = await async_client.get("/api/tickets/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert "total_tickets" in stats

    list_res = await async_client.get("/api/tickets")
    assert list_res.status_code == 200
    assert isinstance(list_res.json(), list)

@pytest.mark.asyncio
async def test_knowledge_base_endpoints(async_client: AsyncClient):
    # List docs
    list_res = await async_client.get("/api/knowledge/list")
    assert list_res.status_code == 200
    assert len(list_res.json()) > 0

    # Index new doc
    new_doc_payload = {
        "title": "Pytest Knowledge Document",
        "category": "Testing",
        "content": "This is a document created during automated testing pipeline."
    }
    create_res = await async_client.post("/api/knowledge/index", json=new_doc_payload)
    assert create_res.status_code == 200
    created_doc = create_res.json()
    assert created_doc["title"] == "Pytest Knowledge Document"

    # Search
    search_res = await async_client.post("/api/knowledge/search", json={"query": "automated testing pipeline", "limit": 2})
    assert search_res.status_code == 200
    assert len(search_res.json()["results"]) > 0
