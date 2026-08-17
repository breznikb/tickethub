import asyncio

from qdrant_client import models
from sqlalchemy import select

from tickethub.core.config import QDRANT_COLLECTION_NAME
from tickethub.core.db import SessionLocal
from tickethub.core.vector_db import qdrant_client
from tickethub.models.ticket import Ticket
from tickethub.services.embeddings import embed_documents
from tickethub.services.vector_store import ensure_ticket_collection


def ticket_to_text(ticket: Ticket) -> str:
    return "\n".join(
        [
            f"Title: {ticket.title}",
            f"Assignee: {ticket.assignee}",
        ]
    )


async def index_tickets() -> int:
    await ensure_ticket_collection()

    async with SessionLocal() as db:
        result = await db.execute(select(Ticket))
        tickets = list(result.scalars().all())

    if not tickets:
        return 0

    texts = [ticket_to_text(ticket) for ticket in tickets]
    vectors = embed_documents(texts)

    points = [
        models.PointStruct(
            id=ticket.id,
            vector=vector,
            payload={
                "ticket_id": ticket.id,
                "title": ticket.title,
                "status": ticket.status,
                "priority": ticket.priority,
                "assignee": ticket.assignee,
            },
        )
        for ticket, vector in zip(tickets, vectors)
    ]

    await qdrant_client.upsert(
        collection_name=QDRANT_COLLECTION_NAME,
        points=points,
        wait=True,
    )

    return len(points)


async def run_indexing() -> int:
    try:
        return await index_tickets()
    finally:
        await qdrant_client.close()


def main() -> None:
    indexed = asyncio.run(run_indexing())
    print(f"Indexed {indexed} tickets")


if __name__ == "__main__":
    main()
