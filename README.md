# TicketHub

TicketHub is a small asynchronous REST API for managing support tickets. It can
also import todos and users from [DummyJSON](https://dummyjson.com/) and convert
them into tickets.

The project is built with FastAPI, SQLAlchemy, Alembic, and SQLite. It includes
Docker support, automated tests, linting, and a GitHub Actions workflow.

## Features

- Create, retrieve, update, list, filter, and search tickets
- Async database access with SQLAlchemy and `aiosqlite`
- Database migrations managed by Alembic
- Idempotent synchronization from DummyJSON
- Interactive OpenAPI documentation provided by FastAPI
- Docker Compose setup for running the complete application

## Requirements

For local development:

- Python 3.11 or newer
- `pip`

Alternatively, install Docker and Docker Compose to run the containerized
application.

## Run with Docker

Build and start the API:

```bash
docker compose up --build
```

The container applies database migrations and, when SYNC_ON_STARTUP=true, attempts to import DummyJSON data before starting the API. A synchronization failure does not prevent the API from starting.

Open the following URLs after startup:

- API: <http://localhost:8000>
- Swagger UI: <http://localhost:8000/docs>
- ReDoc: <http://localhost:8000/redoc>

Stop the application with:

```bash
docker compose down
```

## Run locally

Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate
```

Install the dependencies:

```bash
pip install -r requirements.txt -r requirements-dev.txt
```

Make the source package importable and apply the database migration:

```bash
export PYTHONPATH=src
alembic upgrade head
```

Import tickets from DummyJSON if you want to seed the database:

```bash
python -m tickethub.services.sync
```

Start the development server:

```bash
uvicorn tickethub.main:app --reload
```

The local setup stores data in `tickethub.db` in the project directory by
default.

## Configuration

TicketHub reads the following optional environment variables:

| Variable | Default | Description |
| --- | --- | --- |
| `DATABASE_URL` | `sqlite+aiosqlite:///./tickethub.db` | Async SQLAlchemy database URL |
| `DUMMYJSON_BASE_URL` | `https://dummyjson.com` | Base URL used by the import client |
| `SYNC_ON_STARTUP` | `false` | Attempt DummyJSON synchronization when the container starts |
| `DUMMYJSON_TIMEOUT_SECONDS` | `10` | Timeout for DummyJSON HTTP operations in seconds |

For example:

```bash
export DATABASE_URL="sqlite+aiosqlite:///./local.db"
export DUMMYJSON_BASE_URL="https://dummyjson.com"
```

## API

### Health check

```http
GET /
```

Returns `{"status": "ok"}` when the application is running.

### List tickets

```http
GET /tickets?skip=0&limit=20&status=open&priority=high
```

All query parameters are optional. `limit` has a maximum value of 100.

### Search tickets

```http
GET /tickets/search?q=meeting
```

Search is case-insensitive and matches text contained in the ticket title.

### Get a ticket

```http
GET /tickets/{ticket_id}
```

Returns `404` when the ticket does not exist.

### Create a ticket

```http
POST /tickets
Content-Type: application/json

{
  "title": "Investigate checkout failure",
  "assignee": "alice",
  "status": "open",
  "priority": "high"
}
```

Only `title` and `assignee` are required. `status` defaults to `open`, and
`priority` defaults to `medium`.

### Update a ticket

```http
PATCH /tickets/{ticket_id}
Content-Type: application/json

{
  "status": "closed",
  "priority": "low",
  "assignee": "bob"
}
```

All update fields are optional, and omitted fields remain unchanged.

## DummyJSON synchronization

The synchronization command downloads all todos and users, transforms each todo
into a ticket, and inserts or updates it by ID:

```bash
python -m tickethub.services.sync
```

The transformation uses these rules:

- A completed todo becomes a `closed` ticket; otherwise it becomes `open`.
- The assignee is resolved from the todo's user ID, or set to `unknown` when the
  user cannot be found.
- Priority cycles through `low`, `medium`, and `high` based on the todo ID.
- The original todo object is retained in the ticket's `source_data` field.

Because existing rows are updated, the synchronization can safely be run more
than once.

## Development

Run the test suite:

```bash
pytest -v
```

Run the linter:

```bash
flake8 src tests
```

The GitHub Actions workflow runs both commands for every push and pull request.

## Project structure

```text
.
├── alembic/                    # Migration environment and revisions
├── src/tickethub/
│   ├── api/                    # FastAPI routes
│   ├── core/                   # Configuration and database setup
│   ├── models/                 # SQLAlchemy models
│   ├── schemas/                # Pydantic API schemas
│   ├── services/               # Import client, transformation, and sync
│   └── main.py                 # FastAPI application entry point
├── tests/                      # Unit and API tests
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
