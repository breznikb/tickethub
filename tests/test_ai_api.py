from tickethub.services.vector_store import TicketMatch


async def test_ai_ask_returns_grounded_answer(
    client,
    monkeypatch,
):
    create_response = await client.post(
        "/tickets",
        json={
            "title": "Plan a trip to another country",
            "assignee": "alice",
        },
    )
    ticket_id = create_response.json()["id"]

    async def fake_vector_search(**_kwargs):
        return [
            TicketMatch(
                ticket_id=ticket_id,
                score=0.85,
            )
        ]

    async def fake_generate_answer(question, context):
        assert "trip" in question
        assert f"[Ticket #{ticket_id}]" in context
        assert "Assignee: alice" in context
        return f"Alice owns this task [Ticket #{ticket_id}]."

    monkeypatch.setattr(
        "tickethub.services.rag.search_ticket_vectors",
        fake_vector_search,
    )
    monkeypatch.setattr(
        "tickethub.services.rag.generate_answer",
        fake_generate_answer,
    )

    response = await client.post(
        "/ai/ask",
        json={
            "question": "Who owns the trip ticket?",
            "limit": 3,
        },
    )

    assert response.status_code == 200

    body = response.json()
    assert body["answer"] == (
        f"Alice owns this task [Ticket #{ticket_id}]."
    )
    assert body["sources"] == [
        {
            "id": ticket_id,
            "title": "Plan a trip to another country",
            "score": 0.85,
        }
    ]


async def test_ai_ask_rejects_weak_matches(
    client,
    monkeypatch,
):
    create_response = await client.post(
        "/tickets",
        json={
            "title": "Unrelated ticket",
            "assignee": "bob",
        },
    )
    ticket_id = create_response.json()["id"]

    async def fake_vector_search(**_kwargs):
        return [
            TicketMatch(
                ticket_id=ticket_id,
                score=0.66,
            )
        ]

    async def fail_if_called(**_kwargs):
        raise AssertionError(
            "Ollama should not run for weak matches"
        )

    monkeypatch.setattr(
        "tickethub.services.rag.search_ticket_vectors",
        fake_vector_search,
    )
    monkeypatch.setattr(
        "tickethub.services.rag.generate_answer",
        fail_if_called,
    )

    response = await client.post(
        "/ai/ask",
        json={
            "question": "Account access problem",
        },
    )

    assert response.status_code == 200
    assert response.json() == {
        "answer": "I could not find relevant tickets.",
        "sources": [],
    }


async def test_ai_ask_validates_limit(client):
    response = await client.post(
        "/ai/ask",
        json={
            "question": "Find travel tickets",
            "limit": 20,
        },
    )

    assert response.status_code == 422
