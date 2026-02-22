import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.db.base import Base
from app.core.dependencies import get_db

# Use an in-memory SQLite database for testing.
# By NOT using StaticPool, each connection will get its own private in-memory DB.
TEST_DATABASE_URL = "sqlite+aiosqlite:///"

engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

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
    """Provide a clean database session for each test."""
    async with engine.connect() as conn:
        # Start a transaction for the entire test
        async with conn.begin() as trans:
            # Create tables in this specific connection
            await conn.run_sync(Base.metadata.create_all)
            
            async with TestingSessionLocal(bind=conn) as session:
                yield session
                await session.close()
            
            # Rollback EVERYTHING (including the create_all)
            await trans.rollback()


@pytest_asyncio.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Provide an AsyncClient that uses the test database."""
    def override_get_db():
        yield db

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(
        transport=ASGITransport(app=app), 
        base_url="http://test/api/v1"
    ) as ac:
        yield ac
    
    app.dependency_overrides.clear()
