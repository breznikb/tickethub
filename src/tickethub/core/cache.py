import json
import logging
import redis.asyncio as redis

from tickethub.core.config import REDIS_URL
from redis.exceptions import RedisError


logger = logging.getLogger(__name__)
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

TICKET_CACHE_TTL = 30


def ticket_cache_key(ticket_id: int) -> str:
    return f"ticket:{ticket_id}"


async def get_cached_ticket(ticket_id: int) -> dict | None:
    try:
        cached = await redis_client.get(
            ticket_cache_key(ticket_id)
        )

        if cached is None:
            return None

        return json.loads(cached)
    except (RedisError, json.JSONDecodeError) as exc:
        logger.warning(
            "Ticket cache read failed; using database: "
            "ticket_id=%s error=%s",
            ticket_id,
            exc,
        )
        return None


async def set_cached_ticket(
    ticket_id: int,
    data: dict,
) -> None:
    try:
        await redis_client.set(
            ticket_cache_key(ticket_id),
            json.dumps(data),
            ex=TICKET_CACHE_TTL,
        )
    except RedisError as exc:
        logger.warning(
            "Ticket cache write failed: "
            "ticket_id=%s error=%s",
            ticket_id,
            exc,
        )


async def invalidate_cached_ticket(
    ticket_id: int,
) -> None:
    try:
        await redis_client.delete(
            ticket_cache_key(ticket_id)
        )
    except RedisError as exc:
        logger.warning(
            "Ticket cache invalidation failed: "
            "ticket_id=%s error=%s",
            ticket_id,
            exc,
        )
