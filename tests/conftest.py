import asyncio
import os

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool


os.environ.setdefault(
    "JWT_SECRET_KEY",
    "test-only-secret-key-do-not-use-in-production",
)


from tickethub.core.db import Base, get_db  # noqa: E402
from tickethub.main import app  # noqa: E402


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(autouse=True)
def disable_vector_indexing(monkeypatch):
    async def do_nothing(_ticket):
        return None

    monkeypatch.setattr(
        "tickethub.api.tickets.index_ticket_safely",
        do_nothing,
    )


@pytest.fixture(autouse=True)
def disable_ticket_cache(monkeypatch):
    async def return_cache_miss(_ticket_id):
        return None

    async def do_not_set_cache(_ticket_id, _data):
        return None

    async def do_not_invalidate_cache(_ticket_id):
        return None

    monkeypatch.setattr(
        "tickethub.api.tickets.get_cached_ticket",
        return_cache_miss,
    )
    monkeypatch.setattr(
        "tickethub.api.tickets.set_cached_ticket",
        do_not_set_cache,
    )
    monkeypatch.setattr(
        "tickethub.api.tickets.invalidate_cached_ticket",
        do_not_invalidate_cache,
    )


TEST_DATABASE_URL = "sqlite+aiosqlite://"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestSessionLocal = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
)


async def override_get_db():
    async with TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


@pytest_asyncio.fixture(autouse=True)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

    await test_engine.dispose()


@pytest_asyncio.fixture
async def unauthenticated_client():
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def client(unauthenticated_client):
    register_response = await unauthenticated_client.post(
        "/auth/register",
        json={
            "username": "test-user",
            "password": "test-password",
        },
    )
    assert register_response.status_code == 201

    login_response = await unauthenticated_client.post(
        "/auth/token",
        data={
            "username": "test-user",
            "password": "test-password",
        },
    )
    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    unauthenticated_client.headers["Authorization"] = (
        f"Bearer {token}"
    )

    return unauthenticated_client
