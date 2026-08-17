# TicketHub

Middleware REST service built with FastAPI that ingests "tickets" from the DummyJSON API, stores them in a local database, and exposes read/write endpoints over that local store. Built as the entrance task for the Abysalto AI Academy (Python Developer track).

## Tech stack

- Python 3.11
- FastAPI 0.111
- httpx 0.27
- Pydantic 2.7
- SQLAlchemy 2.x (async)
- Alembic
- pytest
- Docker / docker-compose
- Redis (caching)

## Project structure

```
src/tickethub/
├── api/        # FastAPI routers
├── core/       # config, DB engine/session, Redis cache helpers
├── models/     # SQLAlchemy ORM models
├── schemas/    # Pydantic request/response models
├── services/   # DummyJSON client, transform logic, sync job
└── main.py     # FastAPI app entrypoint
tests/          # pytest unit + integration tests
alembic/        # DB migrations
```

## Environment setup (local, without Docker)

Requires Python 3.11.

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
```

## Configuration

Environment variables (all optional, sensible defaults provided):

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./tickethub.db` | Async SQLAlchemy database URL |
| `DUMMYJSON_BASE_URL` | `https://dummyjson.com` | Base URL for the external DummyJSON source |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL, used for caching ticket detail lookups |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant HTTP endpoint used for vector storage |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Local model used to create ticket and query embeddings |
| `EMBEDDING_CACHE_DIR` | FastEmbed default | Directory used to cache embedding model files |
| `QDRANT_COLLECTION_NAME` | `tickets` | Qdrant collection containing ticket vectors |

## Running locally

Apply database migrations:

```bash
alembic upgrade head
```

Seed the database from DummyJSON:

```bash
PYTHONPATH=src python3.11 -m tickethub.services.sync
```

Start the API:

```bash
uvicorn tickethub.main:app --reload --app-dir src
```

Then open http://127.0.0.1:8000/docs for interactive API docs.

Note: `GET /tickets/{id}` uses Redis for caching. Running locally without Docker requires a Redis instance reachable at `REDIS_URL` (e.g. `docker run -p 6379:6379 redis:7-alpine`), otherwise that endpoint will fail to connect to Redis.

## Running with Docker

```bash
docker compose up --build
```

Builds the image, starts a Redis container alongside the API, runs migrations, seeds the database, and starts the API on http://localhost:8000. The SQLite database persists in the `./data` directory via a mounted volume.

## Running tests

```bash
pytest -v
```

Tests use a separate SQLite database (`test_tickethub.db`) and never touch the real `tickethub.db`.

## Linting

```bash
flake8 src tests
```

## Using the Makefile

| Command | Description |
|---|---|
| `make install` | Install dependencies |
| `make run` | Run the API locally |
| `make migrate` | Apply database migrations |
| `make sync` | Seed/refresh data from DummyJSON |
| `make lint` | Run flake8 |
| `make test` | Run pytest |
| `make docker-build` | Build the Docker image |
| `make docker-up` | Run via Docker Compose |

## API overview

| Method | Endpoint | Description |
|---|---|---|
| GET | `/tickets` | Paginated list, filterable by `status` and `priority` |
| GET | `/tickets/{id}` | Ticket detail, including full original source JSON (cached in Redis for 30s) |
| GET | `/tickets/search?q=` | Search tickets by title |
| POST | `/tickets` | Create a new ticket |
| PATCH | `/tickets/{id}` | Update a ticket's status/priority/assignee (invalidates its cache entry) |

## Design notes

- All read/write endpoints operate against the local database only — DummyJSON is called exclusively during the sync step (startup script / Docker entrypoint), never per-request.
- `priority` is derived from `id % 3` (0=low, 1=medium, 2=high) since DummyJSON's todos have no native priority field.
- The list endpoint's `description` field is the ticket's `title` truncated to 100 characters, since DummyJSON's todos have no separate description field.
- The sync is idempotent (upsert by id), so it's safe to re-run.
- `GET /tickets/{id}` caches its response in Redis for 30 seconds; `PATCH /tickets/{id}` explicitly invalidates that cache entry so updates are reflected immediately instead of waiting for the TTL to expire.

## AI usage disclosure

This project was built interactively with Claude and Codex, used as a step-by-step technical assistant/tutor rather than an autonomous code generator — the author wrote/typed every file, ran every command, and debugged real errors (WSL setup, Docker CLI permissions, line-ending issues in `entrypoint.sh`, flake8 style violations) as they occurred, with Claude providing explanations and next-step guidance at each stage.
