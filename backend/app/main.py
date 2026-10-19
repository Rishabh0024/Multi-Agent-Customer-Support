import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from app.core.config import settings
from app.core.logging import logger
from app.db.database import init_db, get_db_session
from app.services.knowledge_ingestion import seed_knowledge_base

# Routers
from app.api.chat_routes import router as chat_router
from app.api.ticket_routes import router as ticket_router
from app.api.knowledge_routes import router as knowledge_router
from app.api.health_routes import router as health_router

class PingLogFilter(logging.Filter):
    """Filters out ping access logs so container probes never pollute stdout."""
    def filter(self, record: logging.LogRecord) -> bool:
        msg = record.getMessage()
        return "/api/ping" not in msg and "/ping" not in msg

logging.getLogger("uvicorn.access").addFilter(PingLogFilter())

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware enforcing secure reverse proxy and browser protection headers."""
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize Database and Knowledge Seed
    logger.info("Starting Multi-Agent Customer Support Assistant Backend...")
    await init_db()

    # Seed initial enterprise support docs if DB is empty
    async for db in get_db_session():
        await seed_knowledge_base(db)
        break

    yield
    # Shutdown
    logger.info("Shutting down Multi-Agent Customer Support Assistant Backend...")

app = FastAPI(
    title=settings.APP_NAME,
    description="Enterprise Multi-Agent Customer Support System with LangGraph, Qdrant RAG, Sentiment Escalation, and PostgreSQL.",
    version="1.0.0",
    lifespan=lifespan
)

# Security & Reverse Proxy Headers
app.add_middleware(SecurityHeadersMiddleware)

# CORS Middleware (Allows Vercel Frontend and local dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API Routers
app.include_router(chat_router)
app.include_router(ticket_router)
app.include_router(knowledge_router)
app.include_router(health_router)

@app.get("/api/ping", tags=["Health & Status"])
@app.head("/api/ping", tags=["Health & Status"])
async def ping_alias():
    return {"status": "awake", "service": "customer-support-api"}

@app.get("/", tags=["Root"])
async def root(request: Request):
    client_ip = request.headers.get("x-forwarded-for", request.client.host if request.client else "unknown")
    return {
        "service": settings.APP_NAME,
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_url": "/api/health",
        "reverse_proxy_shield": "active",
        "client_ip_detected": client_ip.split(",")[0].strip()
    }

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", settings.PORT))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=settings.DEBUG)
