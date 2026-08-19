from redis.exceptions import RedisError
from sqlalchemy.exc import OperationalError


async def test_health_live(unauthenticated_client):
    response = await unauthenticated_client.get("/health/live")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_health_ready_when_all_dependencies_ok(unauthenticated_client, monkeypatch):
    class WorkingConnection:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def execute(self, *args, **kwargs):
            return None

    class WorkingEngine:
        def connect(self):
            return WorkingConnection()

    async def working_ping():
        return True

    async def working_get_collections():
        return None

    monkeypatch.setattr("tickethub.api.health.engine", WorkingEngine())
    monkeypatch.setattr("tickethub.api.health.redis_client.ping", working_ping)
    monkeypatch.setattr(
        "tickethub.api.health.qdrant_client.get_collections",
        working_get_collections,
     )

    response = await unauthenticated_client.get("/health/ready")

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "checks": {
            "database": "ok",
            "redis": "ok",
            "qdrant": "ok",
        },
    }


async def test_health_ready_when_redis_is_down(unauthenticated_client, monkeypatch):
    async def broken_ping():
        raise RedisError("connection refused")

    monkeypatch.setattr(
        "tickethub.api.health.redis_client.ping",
        broken_ping,
    )

    response = await unauthenticated_client.get("/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["checks"]["redis"].startswith("error:")


async def test_health_ready_when_database_is_down(unauthenticated_client, monkeypatch):
    class BrokenConnection:
        async def __aenter__(self):
            raise OperationalError("connect failed", None, None)

        async def __aexit__(self, *args):
            return False

    class BrokenEngine:
        def connect(self):
            return BrokenConnection()

    monkeypatch.setattr(
        "tickethub.api.health.engine",
        BrokenEngine(),
    )

    response = await unauthenticated_client.get("/health/ready")

    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "unavailable"
    assert body["checks"]["database"].startswith("error:")


async def test_health_ready_when_qdrant_is_down(unauthenticated_client, monkeypatch):
    class WorkingConnection:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *args):
            return False

        async def execute(self, *args, **kwargs):
            return None

    class WorkingEngine:
        def connect(self):
            return WorkingConnection()

    async def working_ping():
        return True

    async def broken_get_collections():
        raise RuntimeError("connection refused")

    monkeypatch.setattr("tickethub.api.health.engine", WorkingEngine())
    monkeypatch.setattr("tickethub.api.health.redis_client.ping", working_ping)
    monkeypatch.setattr(
        "tickethub.api.health.qdrant_client.get_collections",
        broken_get_collections,
    )

    response = await unauthenticated_client.get("/health/ready")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"]["qdrant"].startswith("error:")
    assert body["checks"]["database"] == "ok"
    assert body["checks"]["redis"] == "ok"
