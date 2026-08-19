from fastapi import APIRouter
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError
from sqlalchemy import text

from tickethub.core.cache import redis_client
from tickethub.core.db import engine
from tickethub.core.vector_db import qdrant_client


router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live")
async def live():
    return {"status": "ok"}


@router.get("/ready")
async def ready():
    checks = {}

    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception as exc:
        checks["database"] = f"error: {exc}"

    try:
        await redis_client.ping()
        checks["redis"] = "ok"
    except RedisError as exc:
        checks["redis"] = f"error: {exc}"

    try:
        await qdrant_client.get_collections()
        checks["qdrant"] = "ok"
    except Exception as exc:
        checks["qdrant"] = f"error: {exc}"

    required_ok = checks["database"] == "ok" and checks["redis"] == "ok"
    status_code = 200 if required_ok else 503

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "ok" if required_ok else "unavailable",
            "checks": checks,
        },
    )
