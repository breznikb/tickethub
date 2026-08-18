import logging
from unittest.mock import AsyncMock

import pytest

from tickethub.services import sync


async def test_ticket_creation_is_logged(
    client,
    caplog,
):
    with caplog.at_level(
        logging.INFO,
        logger="tickethub.api.tickets",
    ):
        response = await client.post(
            "/tickets",
            json={
                "title": "Log this ticket",
                "assignee": "alice",
            },
        )

    assert response.status_code == 201

    ticket_id = response.json()["id"]
    assert (
        f"Ticket created: ticket_id={ticket_id}"
        in caplog.text
    )


async def test_sync_failure_is_logged(
    monkeypatch,
    caplog,
):
    async def fail_sync():
        raise RuntimeError("Simulated sync failure")

    monkeypatch.setattr(
        sync,
        "sync_tickets",
        fail_sync,
    )
    monkeypatch.setattr(
        sync.qdrant_client,
        "close",
        AsyncMock(),
    )

    with caplog.at_level(
        logging.ERROR,
        logger="tickethub.services.sync",
    ):
        with pytest.raises(
            RuntimeError,
            match="Simulated sync failure",
        ):
            await sync.sync_and_index()

    assert "Ticket synchronization failed" in caplog.text
