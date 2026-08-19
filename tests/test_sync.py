import asyncio

import pytest

from tickethub.services import sync


async def test_run_periodic_sync_calls_sync_and_sleeps(monkeypatch):
    sync_calls = []

    async def fake_sync_and_index():
        sync_calls.append(1)
        return (0, 0)

    sleep_calls = []

    async def fake_sleep(seconds):
        sleep_calls.append(seconds)
        if len(sleep_calls) >= 2:
            raise asyncio.CancelledError()

    monkeypatch.setattr(sync, "sync_and_index", fake_sync_and_index)
    monkeypatch.setattr(sync.asyncio, "sleep", fake_sleep)

    with pytest.raises(asyncio.CancelledError):
        await sync.run_periodic_sync(42)

    assert sync_calls == [1, 1]
    assert sleep_calls == [42, 42]


async def test_run_periodic_sync_continues_after_failure(monkeypatch):
    call_count = 0

    async def failing_sync_and_index():
        nonlocal call_count
        call_count += 1
        raise RuntimeError("boom")

    sleep_calls = []

    async def fake_sleep(seconds):
        sleep_calls.append(seconds)
        if len(sleep_calls) >= 2:
            raise asyncio.CancelledError()

    monkeypatch.setattr(sync, "sync_and_index", failing_sync_and_index)
    monkeypatch.setattr(sync.asyncio, "sleep", fake_sleep)

    with pytest.raises(asyncio.CancelledError):
        await sync.run_periodic_sync(5)

    assert call_count == 2
