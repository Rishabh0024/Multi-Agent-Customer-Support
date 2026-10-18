from fastapi import APIRouter
from app.core.config import settings
from app.vector_store.qdrant_client import qdrant_store
from app.memory.redis_client import redis_manager

router = APIRouter(prefix="/api/health", tags=["Health & Status"])

@router.get("")
async def check_health():
    """Health check for system components."""
    qdrant_healthy = False
    try:
        if qdrant_store.client:
            qdrant_healthy = True
    except Exception:
        pass

    redis_healthy = False
    try:
        redis_healthy = redis_manager.client.ping()
    except Exception:
        pass

    return {
        "status": "healthy",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "components": {
            "fastapi": "operational",
            "qdrant_vector_store": "operational" if qdrant_healthy else "degraded",
            "redis_cache": "operational" if redis_healthy else "degraded_in_memory_fallback",
            "llm_provider": "gemini_1.5_flash" if settings.GEMINI_API_KEY else ("openai_active" if settings.OPENAI_API_KEY else "mock_heuristic_mode"),
            "database_engine": "postgresql" if "postgresql" in settings.DATABASE_URL else "sqlite_fallback"
        }
    }

@router.get("/ping")
@router.head("/ping")
async def ping_keepalive():
    """Ultra-lightweight endpoint for keep-alive cron jobs.
    Zero DB or vector store overhead; keeps Render instances awake with minimal CPU."""
    return {"status": "awake", "service": "customer-support-api"}

