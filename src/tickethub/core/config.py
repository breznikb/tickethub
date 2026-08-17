import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tickethub.db")

DUMMYJSON_BASE_URL = os.getenv("DUMMYJSON_BASE_URL", "https://dummyjson.com")

DUMMYJSON_TIMEOUT_SECONDS = float(
    os.getenv("DUMMYJSON_TIMEOUT_SECONDS", "10")
)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
