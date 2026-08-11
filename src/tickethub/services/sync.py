import asyncio

from tickethub.core.db import SessionLocal
from tickethub.models.ticket import Ticket
from tickethub.services.dummyjson_client import fetch_todos, fetch_users
from tickethub.services.transform import transform_todo_to_ticket


async def sync_tickets() -> int:
    todos = await fetch_todos()
    users = await fetch_users()
    users_by_id = {user["id"]: user for user in users}

    async with SessionLocal() as db:
        count = 0
        for todo in todos:
            data = transform_todo_to_ticket(todo, users_by_id)
            existing = await db.get(Ticket, data["id"])
            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
            else:
                db.add(Ticket(**data))
            count += 1
        await db.commit()
    return count


if __name__ == "__main__":
    synced = asyncio.run(sync_tickets())
    print(f"Synced {synced} tickets")
