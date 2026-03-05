import os
import pytest
import pytest_asyncio

# use sqlite for tests
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"

from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from backend.db.session import Base, get_db
from backend.main import app

# in-memory SQLite for tests
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"

engine_test = create_async_engine(TEST_DB_URL, echo=False)
TestSession = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)


async def override_get_db():
    async with TestSession() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client(monkeypatch):
    import backend.services.task_service as svc

    # stub enqueue
    async def fake_enqueue(task_id, title, payload):
        pass

    monkeypatch.setattr(svc, "enqueue_task", fake_enqueue)

    # stub redis cache
    async def fake_get_cached(task_id):
        return None

    async def fake_cache_task(task_id, data):
        pass

    monkeypatch.setattr(svc, "get_cached_task", fake_get_cached)
    monkeypatch.setattr(svc, "cache_task", fake_cache_task)

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
