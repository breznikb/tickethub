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
    await client.post("/tickets", json={"title": "Closed one", "assignee": "bob", "status": "closed"})

    response = await client.get("/tickets", params={"status": "closed"})
    assert response.status_code == 200
    assert all(t["status"] == "closed" for t in response.json())


async def test_search_tickets_by_title(client):
    await client.post("/tickets", json={"title": "Unique searchable title", "assignee": "carol"})

    response = await client.get("/tickets/search", params={"q": "searchable"})
    assert response.status_code == 200
    assert any("searchable" in t["title"].lower() for t in response.json())