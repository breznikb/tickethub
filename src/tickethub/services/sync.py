import asyncio

import logging

from tickethub.core.db import SessionLocal
from tickethub.core.vector_db import qdrant_client
from tickethub.models.ticket import Ticket
from tickethub.services.dummyjson_client import (
    fetch_todos,
    fetch_users,
)
from tickethub.services.index_tickets import index_tickets
from tickethub.services.transform import transform_todo_to_ticket
from tickethub.core.logging_config import configure_logging


logger = logging.getLogger(__name__)


async def sync_tickets() -> int:
    todos = await fetch_todos()
    users = await fetch_users()
    users_by_id = {
        user["id"]: user
        for user in users
    }

    async with SessionLocal() as db:
        count = 0

        for todo in todos:
            data = transform_todo_to_ticket(
                todo,
                users_by_id,
            )
            existing = await db.get(Ticket, data["id"])

            if existing:
                for key, value in data.items():
                    setattr(existing, key, value)
            else:
                db.add(Ticket(**data))

            count += 1

        await db.commit()

    return count


async def sync_and_index() -> tuple[int, int]:
    logger.info("Ticket synchronization started")

    try:
        synced = await sync_tickets()
        indexed = await index_tickets()

        logger.info(
            "Ticket synchronization completed: "
            "synced=%s indexed=%s",
            synced,
            indexed,
        )

        return synced, indexed
    except Exception:
        logger.exception(
            "Ticket synchronization failed"
        )
        raise
    finally:
        await qdrant_client.close()


def main() -> None:
    configure_logging()

    try:
        asyncio.run(sync_and_index())
    except Exception as exc:
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
