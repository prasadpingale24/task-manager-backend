import asyncio
import os
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from urllib.parse import quote_plus

from app.main import app
from app.db.base import Base
from app.core.dependencies import get_db
from app.db import session as db_session

# --- Windows Compatibility ---
if os.name == 'nt':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# --- Configuration ---

def get_test_db_url():
    user = os.getenv("POSTGRES_USER", "postgres")
    password = quote_plus(os.getenv("POSTGRES_PASSWORD", "postgres"))
    host = os.getenv("POSTGRES_HOST", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    db = os.getenv("POSTGRES_DB", "task_manager_test")
    return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"

# --- Fixtures ---

@pytest_asyncio.fixture
async def engine():
    """Function-scoped engine to ensure loop consistency."""
    engine = create_async_engine(get_test_db_url(), echo=False)
    db_session.engine = engine
    yield engine
    await engine.dispose()

@pytest_asyncio.fixture(autouse=True)
async def setup_test_db(engine):
    """Ensure tables exist for each test. Function-scoped for consistency."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # No drop_all here for speed, just rely on create_all being safe or recreate DB if needed

@pytest_asyncio.fixture
async def db(engine) -> AsyncGenerator[AsyncSession, None]:
    """Function-scoped session with transactional rollback."""
    async with engine.connect() as connection:
        transaction = await connection.begin()
        
        session = AsyncSession(
            bind=connection,
            expire_on_commit=False,
            autocommit=False,
            autoflush=False,
        )
        
        yield session
        
        await session.close()
        await transaction.rollback()

@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """AsyncClient with DB dependency override."""
    
    async def _get_test_db():
        yield db

    app.dependency_overrides[get_db] = _get_test_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test/api/v1"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()
