#!/bin/sh
set -e

alembic upgrade head

if [ "${SYNC_ON_STARTUP:-false}" = "true" ]; then
    echo "Synchronizing tickets from DummyJSON..."

    if ! python -m tickethub.services.sync; then
        echo "Warning: DummyJSON synchronization failed; starting API without syncing." >&2
    fi
fi

exec uvicorn tickethub.main:app --host 0.0.0.0 --port 8000
