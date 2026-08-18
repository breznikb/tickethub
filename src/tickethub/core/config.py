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

OLLAMA_URL = os.getenv(
    "OLLAMA_URL",
    "http://localhost:11434",
)

OLLAMA_MODEL = os.getenv(
    "OLLAMA_MODEL",
    "gemma3:1b",
)

OLLAMA_TIMEOUT_SECONDS = float(
    os.getenv("OLLAMA_TIMEOUT_SECONDS", "60"),
)

RAG_MIN_RELEVANCE_SCORE = float(
    os.getenv("RAG_MIN_RELEVANCE_SCORE", "0.70")
)

JWT_SECRET_KEY = os.environ["JWT_SECRET_KEY"]
JWT_ALGORITHM = "HS256"
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = 30

RATE_LIMIT_DEFAULT = os.getenv(
    "RATE_LIMIT_DEFAULT",
    "60/minute",
)

RATE_LIMIT_LOGIN = os.getenv(
    "RATE_LIMIT_LOGIN",
    "5/minute",
)

RATE_LIMIT_ENABLED = os.getenv(
    "RATE_LIMIT_ENABLED",
    "true",
).lower() in {"1", "true", "yes"}

LOG_LEVEL = os.getenv(
    "LOG_LEVEL",
    "INFO",
).upper()
