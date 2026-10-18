import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator

class Settings(BaseSettings):
    APP_NAME: str = "Multi-Agent Customer Support Assistant"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = int(os.environ.get("PORT", 8000))
    HOST: str = "0.0.0.0"

    # CORS & Security
    CORS_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "https://*.vercel.app",
        "https://*.onrender.com",
        "*"
    ]
    ALLOWED_HOSTS: List[str] = ["*"]

    # PostgreSQL Database (NeonDB / Local)
    # Format: postgresql+asyncpg://user:password@host/dbname?sslmode=require
    DATABASE_URL: str = "sqlite+aiosqlite:///./customersupport_local.db"
    DATABASE_SYNC_URL: str = "sqlite:///./customersupport_local.db"
    SQLITE_FALLBACK: bool = True

    # Redis Cache & Memory (Upstash / Local)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_FALLBACK_MEMORY: bool = True

    # Qdrant Vector Store (Qdrant Cloud / Local)
    QDRANT_URL: str = "memory"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION_NAME: str = "support_knowledge"
    QDRANT_IN_MEMORY_FALLBACK: bool = True

    # LLM Provider Selection ("gemini" or "openai")
    LLM_PROVIDER: str = "gemini"

    # Google Gemini Settings (Google AI Studio Free Tier)
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-flash-latest"
    GEMINI_EMBEDDING_MODEL: str = "models/gemini-embedding-001"

    # OpenRouter Settings (Free Cloud LLMs: LLaMA 3.3, Gemini, DeepSeek R1, Qwen)
    OPENROUTER_API_KEY: str = ""
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"

    # Groq Cloud Settings (Ultra-fast Free LLaMA 3.3)
    GROQ_API_KEY: str = ""
    GROQ_BASE_URL: str = "https://api.groq.com/openai/v1"

    # OpenAI Settings (Alternative)
    OPENAI_API_KEY: str = ""
    LLM_MODEL: str = "gpt-4o-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-small"
    LLM_TEMPERATURE: float = 0.2

    # Agent Thresholds
    SENTIMENT_ESCALATION_THRESHOLD: float = 0.35  # Threshold <= 0.35 triggers human escalation
    MAX_HISTORY_TURNS: int = 20

    model_config = SettingsConfigDict(
        env_file=(".env", "backend/.env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @field_validator("CORS_ORIGINS", mode="before")
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, list):
            return v
        return ["*"]

    @field_validator("DATABASE_URL", mode="before")
    def normalize_database_url(cls, v: str) -> str:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v and v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

settings = Settings()
