async def test_stats_requires_authentication(
    unauthenticated_client,
):
    response = await unauthenticated_client.get("/stats")

    assert response.status_code == 401


async def test_stats_returns_zeroes_when_empty(client):
    response = await client.get("/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total_tickets": 0,
        "by_status": {
            "open": 0,
            "closed": 0,
        },
        "by_priority": {
            "low": 0,
            "medium": 0,
            "high": 0,
        },
    }


async def test_stats_aggregates_tickets(client):
    tickets = [
        {
            "title": "Open high priority",
            "assignee": "alice",
            "status": "open",
            "priority": "high",
        },
        {
            "title": "Open low priority",
            "assignee": "bob",
            "status": "open",
            "priority": "low",
        },
        {
            "title": "Closed high priority",
            "assignee": "alice",
            "status": "closed",
            "priority": "high",
        },
    ]

    for ticket in tickets:
        response = await client.post(
            "/tickets",
            json=ticket,
        )
        assert response.status_code == 201

    response = await client.get("/stats")

    assert response.status_code == 200
    assert response.json() == {
        "total_tickets": 3,
        "by_status": {
            "open": 2,
            "closed": 1,
        },
        "by_priority": {
            "low": 1,
            "medium": 0,
            "high": 2,
        },
    }
