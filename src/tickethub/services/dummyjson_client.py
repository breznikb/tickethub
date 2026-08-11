import httpx

from tickethub.core.config import DUMMYJSON_BASE_URL


async def fetch_todos() -> list[dict]:
    async with httpx.AsyncClient(base_url=DUMMYJSON_BASE_URL) as client:
        response = await client.get("/todos", params={"limit": 0})
        response.raise_for_status()
        return response.json()["todos"]


async def fetch_users() -> list[dict]:
    async with httpx.AsyncClient(base_url=DUMMYJSON_BASE_URL) as client:
        response = await client.get("/users", params={"limit": 0})
        response.raise_for_status()
        return response.json()["users"]
