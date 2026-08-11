#!/bin/sh
set -e

alembic upgrade head
python -m tickethub.services.sync

exec uvicorn tickethub.main:app --host 0.0.0.0 --port 8000