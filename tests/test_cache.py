import logging
from unittest.mock import AsyncMock

from redis.exceptions import RedisError

from tickethub.core import cache


async def test_cache_read_failure_returns_cache_miss(
    monkeypatch,
    caplog,
):
    monkeypatch.setattr(
        cache.redis_client,
        "get",
        AsyncMock(
            side_effect=RedisError("Redis unavailable"),
        ),
    )

    with caplog.at_level(
        logging.WARNING,
        logger="tickethub.core.cache",
    ):
        result = await cache.get_cached_ticket(23)

    assert result is None
    assert "Ticket cache read failed" in caplog.text


async def test_cache_write_failures_do_not_raise(
    monkeypatch,
    caplog,
):
    monkeypatch.setattr(
        cache.redis_client,
        "set",
        AsyncMock(
            side_effect=RedisError("Redis unavailable"),
        ),
    )
    monkeypatch.setattr(
        cache.redis_client,
        "delete",
        AsyncMock(
            side_effect=RedisError("Redis unavailable"),
        ),
    )

    with caplog.at_level(
        logging.WARNING,
        logger="tickethub.core.cache",
    ):
        await cache.set_cached_ticket(23, {"id": 23})
        await cache.invalidate_cached_ticket(23)

    assert "Ticket cache write failed" in caplog.text
    assert "Ticket cache invalidation failed" in caplog.text


async def test_invalid_cached_json_returns_cache_miss(
    monkeypatch,
    caplog,
):
    monkeypatch.setattr(
        cache.redis_client,
        "get",
        AsyncMock(return_value="not-valid-json"),
    )

    with caplog.at_level(
        logging.WARNING,
        logger="tickethub.core.cache",
    ):
        result = await cache.get_cached_ticket(23)

    assert result is None
    assert "Ticket cache read failed" in caplog.text
