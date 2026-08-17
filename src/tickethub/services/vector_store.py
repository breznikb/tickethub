from qdrant_client import models

from tickethub.core.config import (
    EMBEDDING_VECTOR_SIZE,
    QDRANT_COLLECTION_NAME,
)
from tickethub.core.vector_db import qdrant_client


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
