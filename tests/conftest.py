import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from app.main import app
from app.db.base import Base
from app.core.dependencies import get_db


# Build a PostgreSQL test URL from environment variables (same pattern as app/core/config.py).
# Falls back to localhost defaults for local development.
_pg_user = os.getenv("POSTGRES_USER", "postgres")
_pg_pass = os.getenv("POSTGRES_PASSWORD", "postgres")
_pg_host = os.getenv("POSTGRES_HOST", "localhost")
_pg_port = os.getenv("POSTGRES_PORT", "5432")
_pg_db = os.getenv("POSTGRES_DB", "task_manager_test")

TEST_DATABASE_URL = f"postgresql+asyncpg://{_pg_user}:{_pg_pass}@{_pg_host}:{_pg_port}/{_pg_db}"

engine = create_async_engine(TEST_DATABASE_URL)

TestingSessionLocal = async_sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def db() -> AsyncGenerator[AsyncSession, None]:
    """Provide a clean database session for each test.

    Creates all tables before the test, yields a session,
    then drops all tables after the test for full isolation.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session
        await session.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an AsyncClient that uses the test database."""
    async def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test/api/v1"
    ) as ac:
        yield ac

    app.dependency_overrides.clear()
