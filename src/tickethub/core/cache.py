import json

import redis.asyncio as redis

from tickethub.core.config import REDIS_URL

redis_client = redis.from_url(REDIS_URL, decode_responses=True)

TICKET_CACHE_TTL = 30


def ticket_cache_key(ticket_id: int) -> str:
    return f"ticket:{ticket_id}"


async def get_cached_ticket(ticket_id: int) -> dict | None:
    cached = await redis_client.get(ticket_cache_key(ticket_id))
    if cached is None:
        return None
    return json.loads(cached)


async def set_cached_ticket(ticket_id: int, data: dict) -> None:
    await redis_client.set(ticket_cache_key(ticket_id), json.dumps(data), ex=TICKET_CACHE_TTL)


async def invalidate_cached_ticket(ticket_id: int) -> None:
    await redis_client.delete(ticket_cache_key(ticket_id))
