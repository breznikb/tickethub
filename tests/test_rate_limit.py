async def test_login_rate_limit(unauthenticated_client):
    login_data = {
        "username": "nonexistent",
        "password": "wrong-password",
    }

    for _ in range(5):
        response = await unauthenticated_client.post(
            "/auth/token",
            data=login_data,
        )
        assert response.status_code == 401

    response = await unauthenticated_client.post(
        "/auth/token",
        data=login_data,
    )

    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["error"]


async def test_default_rate_limit(unauthenticated_client):
    for _ in range(60):
        response = await unauthenticated_client.get("/")
        assert response.status_code == 200

    response = await unauthenticated_client.get("/")

    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["error"]
