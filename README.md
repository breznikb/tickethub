# TicketHub

Middleware REST service built with FastAPI that ingests "tickets" from the DummyJSON API, stores them locally, and exposes authenticated read/write, semantic search, and AI question-answering endpoints. Built as the entrance task for the Abysalto AI Academy (Python Developer track).

## Tech stack

- Python 3.11
- FastAPI 0.111
- httpx 0.27
- Pydantic 2.7
- SQLAlchemy 2.x (async)
- Alembic
- JWT bearer authentication with PyJWT
- Argon2 password hashing with pwdlib
- pytest
- Docker / docker-compose
- Redis (caching)
- Qdrant (vector storage)
- FastEmbed (local embeddings)
- Ollama with Gemma 3 (local question answering)

## Project structure

```
src/tickethub/
├── api/        # Authentication, ticket, and AI routers
├── core/       # Configuration, DB, security, Redis, and Qdrant helpers
├── models/     # Ticket and user SQLAlchemy ORM models
├── schemas/    # Pydantic request/response models
├── services/   # DummyJSON sync, vector search, and local AI services
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

Most environment variables have local defaults. `JWT_SECRET_KEY` is required.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./tickethub.db` | Async SQLAlchemy database URL |
| `DUMMYJSON_BASE_URL` | `https://dummyjson.com` | Base URL for the external DummyJSON source |
| `REDIS_URL` | `redis://localhost:6379/0` | Redis connection URL, used for caching ticket detail lookups |
| `QDRANT_URL` | `http://localhost:6333` | Qdrant HTTP endpoint used for vector storage |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | Local model used to create ticket and query embeddings |
| `EMBEDDING_CACHE_DIR` | FastEmbed default | Directory used to cache embedding model files |
| `QDRANT_COLLECTION_NAME` | `tickets` | Qdrant collection containing ticket vectors |
| `OLLAMA_URL` | `http://localhost:11434` | Ollama HTTP endpoint |
| `OLLAMA_MODEL` | `gemma3:1b` | Local language model used for answers |
| `OLLAMA_TIMEOUT_SECONDS` | `60` | Maximum wait for local model responses |
| `RAG_MIN_RELEVANCE_SCORE` | `0.70` | Minimum vector score accepted as RAG context |
| `JWT_SECRET_KEY` | Required | Secret used to sign and verify JWT access tokens |
| `JWT_ALGORITHM` | `HS256` (code constant) | JWT signing algorithm |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `30` (code constant) | Access-token lifetime in minutes |

Generate a secret for local development:

```bash
openssl rand -hex 32
```

Create an ignored `.env` file and paste the generated value:

```dotenv
JWT_SECRET_KEY=replace-with-the-generated-value
```

Never commit `.env` or use the local development secret in production.

## Running locally

Start Redis, Qdrant, and Ollama:

```bash
docker compose up -d redis qdrant ollama
```

Load the local environment:

```bash
set -a
source .env
set +a
```

Apply database migrations:

```bash
alembic upgrade head
```

Seed the database from DummyJSON:

```bash
PYTHONPATH=src python3.11 -m tickethub.services.sync
```

Start the API (the environment can alternatively be loaded with Uvicorn's `--env-file .env` option):

```bash
uvicorn tickethub.main:app --reload --app-dir src
```

Then open http://127.0.0.1:8000/docs for interactive API docs.

Note: `GET /tickets/{id}` uses Redis for caching. Running locally without Docker requires a Redis instance reachable at `REDIS_URL` (e.g. `docker run -p 6379:6379 redis:7-alpine`), otherwise that endpoint will fail to connect to Redis.

## Running with Docker

Start Ollama and download the local language model once:

```bash
docker compose up -d ollama
docker compose exec ollama ollama pull gemma3:1b
```

Start the complete application:

```bash
docker compose up --build
```

This builds the image, starts Redis, Qdrant, Ollama, and the API, applies migrations, and serves the API on http://localhost:8000. The SQLite database persists in the `./data` directory, while named Docker volumes preserve vectors, embedding models, and the Ollama model.

Docker Compose reads the project's `.env` file and passes `JWT_SECRET_KEY` to the API container.

Index stored tickets in Qdrant:

```bash
docker compose run --rm --entrypoint python api \
  -m tickethub.services.index_tickets
```

## Authentication

Register a local user:

```bash
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"secret123"}'
```

Request an access token. The OAuth2 password flow uses form data rather than JSON:

```bash
curl -X POST http://127.0.0.1:8000/auth/token \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=alice&password=secret123"
```

Use the returned token to access protected endpoints:

```bash
curl http://127.0.0.1:8000/tickets \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

In the interactive API documentation, register a user through `/auth/register`, click **Authorize**, and enter the same username and password. Ticket and AI endpoints require a valid bearer token.

## Running tests

```bash
pytest -v
```

Tests use an in-memory SQLite database and never touch the real `tickethub.db`. The shared test client registers and authenticates a test user, while Redis caching and background vector indexing are replaced with test doubles.

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
| POST | `/auth/register` | Register a local user with an Argon2-hashed password |
| POST | `/auth/token` | Authenticate with OAuth2 form data and receive a JWT access token |
| GET | `/tickets` | Protected; paginated list, filterable by `status` and `priority` |
| GET | `/tickets/{id}` | Protected; ticket detail, including full original source JSON (cached in Redis for 30s) |
| GET | `/tickets/search?q=` | Protected; search tickets by title |
| GET | `/tickets/semantic-search?q=` | Protected; semantic similarity search with optional filters |
| GET | `/stats` | Protected; aggregate ticket counts by status and priority |
| POST | `/tickets` | Protected; create a new ticket |
| PATCH | `/tickets/{id}` | Protected; update a ticket and invalidate its cache entry |
| POST | `/ai/ask` | Protected; answer questions using relevant tickets and return supporting sources |

## Design notes

- All read/write endpoints operate against the local database only — DummyJSON is called exclusively during the sync step (startup script / Docker entrypoint), never per-request.
- Users register locally. Passwords are stored as Argon2 hashes, and successful login issues a signed HS256 JWT containing the user ID and expiration time.
- Ticket and AI routes validate the bearer token and reload the referenced user from SQLite before processing a request.
- `priority` is derived from `id % 3` (0=low, 1=medium, 2=high) since DummyJSON's todos have no native priority field.
- The list endpoint's `description` field is the ticket's `title` truncated to 100 characters, since DummyJSON's todos have no separate description field.
- The sync is idempotent (upsert by id), so it's safe to re-run.
- `GET /tickets/{id}` caches its response in Redis for 30 seconds; `PATCH /tickets/{id}` explicitly invalidates that cache entry so updates are reflected immediately instead of waiting for the TTL to expire.
- `GET /stats` calculates ticket totals directly from SQLite and returns counts grouped by status and priority, including zero values for categories with no tickets.
- Ticket creation and updates refresh their Qdrant vectors through an in-process background task. The full indexing command can repair the vector index if Qdrant was unavailable during a write.
- The AI endpoint retrieves relevant tickets from Qdrant, reloads their authoritative data from SQLite, and gives only that context to the local Gemma model.
- Matches below `RAG_MIN_RELEVANCE_SCORE` are rejected so unrelated tickets do not trigger an AI-generated answer.

## AI usage disclosure

This project was built interactively with Claude and Codex, used as a step-by-step technical assistant/tutor rather than an autonomous code generator — the author wrote/typed every file, ran every command, and debugged real errors (WSL setup, Docker CLI permissions, line-ending issues in `entrypoint.sh`, flake8 style violations) as they occurred, with Claude providing explanations and guidance at each stage.
