import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tickethub.db")

DUMMYJSON_BASE_URL = os.getenv("DUMMYJSON_BASE_URL", "https://dummyjson.com")

DUMMYJSON_TIMEOUT_SECONDS = float(
    os.getenv("DUMMYJSON_TIMEOUT_SECONDS", "10")
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")

EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "BAAI/bge-small-en-v1.5",
)

EMBEDDING_CACHE_DIR = os.getenv("EMBEDDING_CACHE_DIR")

QDRANT_COLLECTION_NAME = os.getenv(
    "QDRANT_COLLECTION_NAME",
    "tickets",
)

EMBEDDING_VECTOR_SIZE = 384
