import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine
from app.core.config import settings
from app.core.logging import logger

Base = declarative_base()

# Primary async engine
engine = None
AsyncSessionLocal = None

def get_engine():
    global engine, AsyncSessionLocal
    if engine is not None:
        return engine

    database_url = settings.DATABASE_URL
    connect_args = {}
    if "sslmode=require" in database_url or "ssl=require" in database_url or "neon.tech" in database_url:
        database_url = database_url.replace("?sslmode=require", "").replace("&sslmode=require", "")
        database_url = database_url.replace("?ssl=require", "").replace("&ssl=require", "")
        connect_args["ssl"] = True

    try:
        # Test connection or configure
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            connect_args=connect_args,
            future=True
        )
        AsyncSessionLocal = async_sessionmaker(
            bind=engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False
        )
        logger.info(f"Initialized Database Engine with URL: {database_url.split('@')[-1] if '@' in database_url else database_url}")
    except Exception as e:
        logger.warning(f"Could not connect to primary PostgreSQL database ({e}).")
        if settings.SQLITE_FALLBACK:
            sqlite_url = "sqlite+aiosqlite:///./customersupport_local.db"
            logger.info(f"Falling back to local SQLite: {sqlite_url}")
            engine = create_async_engine(sqlite_url, echo=False)
            AsyncSessionLocal = async_sessionmaker(
                bind=engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
        else:
            raise e
    return engine

async def init_db():
    """Initializes tables asynchronously."""
    global engine, AsyncSessionLocal
    get_engine()
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables initialized successfully.")
    except Exception as e:
        logger.error(f"Error initializing database tables: {e}")
        # Try local fallback if postgres failed during run
        if settings.SQLITE_FALLBACK and "sqlite" not in str(engine.url):
            logger.warning("Switching to SQLite fallback engine...")
            engine = create_async_engine("sqlite+aiosqlite:///./customersupport_local.db", echo=False)
            AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info("SQLite fallback tables initialized.")

async def get_db_session():
    """Dependency for yielding async database sessions."""
    get_engine()
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
