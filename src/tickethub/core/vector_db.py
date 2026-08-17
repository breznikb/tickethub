from qdrant_client import AsyncQdrantClient

from tickethub.core.config import QDRANT_URL


qdrant_client = AsyncQdrantClient(url=QDRANT_URL)
