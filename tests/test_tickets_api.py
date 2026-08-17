from tickethub.services.vector_store import TicketMatch


async def test_semantic_search_returns_sqlite_ticket(
    client,
    monkeypatch,
):
    create_response = await client.post(
        "/tickets",
        json={
            "title": "User cannot access account",
            "assignee": "alice",
        },
    )
    ticket_id = create_response.json()["id"]

    async def fake_vector_search(
        query,
        limit,
        status,
        priority,
    ):
        assert query == "login problem"
        assert limit == 3
        assert status == "open"
        assert priority is None

        return [
            TicketMatch(
                ticket_id=ticket_id,
                score=0.91,
            )
        ]

    monkeypatch.setattr(
        "tickethub.api.tickets.search_ticket_vectors",
        fake_vector_search,
    )

    response = await client.get(
        "/tickets/semantic-search",
        params={
            "q": "login problem",
            "limit": 3,
            "status": "open",
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert len(body) == 1
    assert body[0]["id"] == ticket_id
    assert body[0]["title"] == "User cannot access account"
    assert body[0]["score"] == 0.91


async def test_ticket_writes_schedule_vector_indexing(
    client,
    monkeypatch,
):
    indexed_tickets = []

    async def record_indexed_ticket(ticket):
        indexed_tickets.append(
            {
                "id": ticket.id,
                "status": ticket.status,
                "assignee": ticket.assignee,
            }
        )

    monkeypatch.setattr(
        "tickethub.api.tickets.index_ticket_safely",
        record_indexed_ticket,
    )

    create_response = await client.post(
        "/tickets",
        json={
            "title": "Index this ticket",
            "assignee": "alice",
        },
    )

    assert create_response.status_code == 201
    ticket_id = create_response.json()["id"]

    assert indexed_tickets == [
        {
            "id": ticket_id,
            "status": "open",
            "assignee": "alice",
        }
    ]

    indexed_tickets.clear()

    patch_response = await client.patch(
        f"/tickets/{ticket_id}",
        json={"status": "closed"},
    )

    assert patch_response.status_code == 200
    assert indexed_tickets == [
        {
            "id": ticket_id,
            "status": "closed",
            "assignee": "alice",
        }
    ]


async def test_semantic_search_rejects_invalid_status(client):
    response = await client.get(
        "/tickets/semantic-search",
        params={
            "q": "login problem",
            "status": "pending",
        },
    )

    assert response.status_code == 422


async def test_create_and_get_ticket(client):
    response = await client.post(
        "/tickets", json={"title": "New ticket", "assignee": "benjamin"}
    )
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == "New ticket"
    assert created["status"] == "open"

    response = await client.get(f"/tickets/{created['id']}")
    assert response.status_code == 200
    assert response.json()["assignee"] == "benjamin"


async def test_patch_ticket_updates_only_given_fields(client):
    create_resp = await client.post(
        "/tickets", json={"title": "Patch me", "assignee": "alice"}
    )
    ticket_id = create_resp.json()["id"]

    patch_resp = await client.patch(f"/tickets/{ticket_id}", json={"status": "closed"})
    assert patch_resp.status_code == 200
    body = patch_resp.json()
    assert body["status"] == "closed"
    assert body["assignee"] == "alice"  # untouched by the patch


async def test_get_nonexistent_ticket_returns_404(client):
    response = await client.get("/tickets/99999")
    assert response.status_code == 404


async def test_list_tickets_filters_by_status(client):
    await client.post("/tickets", json={"title": "Open one", "assignee": "bob", "status": "open"})
    await client.post(
        "/tickets", json={"title": "Closed one", "assignee": "bob", "status": "closed"}
        )

    response = await client.get("/tickets", params={"status": "closed"})
    assert response.status_code == 200
    assert all(t["status"] == "closed" for t in response.json())


async def test_search_tickets_by_title(client):
    await client.post("/tickets", json={"title": "Unique searchable title", "assignee": "carol"})

    response = await client.get("/tickets/search", params={"q": "searchable"})
    assert response.status_code == 200
    assert any("searchable" in t["title"].lower() for t in response.json())


async def test_create_rejects_invalid_status(client):
    response = await client.post(
        "/tickets",
        json={
            "title": "Invalid status",
            "assignee": "alice",
            "status": "pending",
        },
    )

    assert response.status_code == 422


async def test_create_rejects_invalid_priority(client):
    response = await client.post(
        "/tickets",
        json={
            "title": "Invalid priority",
            "assignee": "alice",
            "priority": "urgent",
        },
    )

    assert response.status_code == 422


async def test_patch_rejects_explicit_null(client):
    create_response = await client.post(
        "/tickets",
        json={"title": "Keep valid", "assignee": "alice"},
    )
    ticket_id = create_response.json()["id"]

    response = await client.patch(
        f"/tickets/{ticket_id}",
        json={"status": None},
    )

    assert response.status_code == 422
