import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./tickethub.db")

DUMMYJSON_BASE_URL = os.getenv("DUMMYJSON_BASE_URL", "https://dummyjson.com")

DUMMYJSON_TIMEOUT_SECONDS = float(
    os.getenv("DUMMYJSON_TIMEOUT_SECONDS", "10")
)
