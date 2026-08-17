import asyncio
from dataclasses import dataclass

from qdrant_client import models

from tickethub.core.config import (
    EMBEDDING_VECTOR_SIZE,
    QDRANT_COLLECTION_NAME,
)
from tickethub.core.vector_db import qdrant_client
from tickethub.services.embeddings import embed_query


@dataclass(frozen=True)
class TicketMatch:
    ticket_id: int
    score: float


async def ensure_ticket_collection() -> None:
    exists = await qdrant_client.collection_exists(
        collection_name=QDRANT_COLLECTION_NAME,
    )

    if exists:
        return

    await qdrant_client.create_collection(
        collection_name=QDRANT_COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=EMBEDDING_VECTOR_SIZE,
            distance=models.Distance.COSINE,
        ),
    )


async def search_ticket_vectors(
    query: str,
    limit: int = 10,
    status: str | None = None,
    priority: str | None = None,
) -> list[TicketMatch]:
    query_vector = await asyncio.to_thread(embed_query, query)

    conditions = []

    if status:
        conditions.append(
            models.FieldCondition(
                key="status",
                match=models.MatchValue(value=status),
            )
        )

    if priority:
        conditions.append(
            models.FieldCondition(
                key="priority",
                match=models.MatchValue(value=priority),
            )
        )

    query_filter = (
        models.Filter(must=conditions)
        if conditions
        else None
    )

    result = await qdrant_client.query_points(
        collection_name=QDRANT_COLLECTION_NAME,
        query=query_vector,
        query_filter=query_filter,
        limit=limit,
        with_payload=False,
    )

    return [
        TicketMatch(
            ticket_id=int(point.id),
            score=point.score,
        )
        for point in result.points
    ]
