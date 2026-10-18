import os
import sys
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Set backend path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend")))

# Force test environment variables
os.environ["APP_ENV"] = "test"
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///./test_customer_support.db"
os.environ["SQLITE_FALLBACK"] = "True"
os.environ["REDIS_URL"] = "redis://localhost:6379/0"
os.environ["REDIS_FALLBACK_MEMORY"] = "True"
os.environ["QDRANT_URL"] = "memory"
os.environ["QDRANT_IN_MEMORY_FALLBACK"] = "True"
os.environ["OPENAI_API_KEY"] = ""
os.environ["GEMINI_API_KEY"] = ""

from app.main import app
from app.db.database import init_db, get_db_session
from app.services.knowledge_ingestion import seed_knowledge_base

_db_initialized = False

@pytest_asyncio.fixture(autouse=True)
async def setup_test_database():
    global _db_initialized
    if not _db_initialized:
        await init_db()
        async for db in get_db_session():
            await seed_knowledge_base(db)
            break
        _db_initialized = True
    yield

@pytest_asyncio.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
