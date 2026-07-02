import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_register_and_login():
    async with AsyncClient(app=app, base_url="http://test") as client:
        reg = await client.post("/auth/register", json={
            "email": "test@example.com", "username": "testuser",
            "password": "secret123", "full_name": "Test User",
        })
        assert reg.status_code == 201
        login = await client.post("/auth/login", data={"username": "test@example.com", "password": "secret123"})
        assert login.status_code == 200
        tokens = login.json()
        assert "access_token" in tokens and "refresh_token" in tokens


@pytest.mark.asyncio
async def test_login_wrong_password():
    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.post("/auth/login", data={"username": "x@x.com", "password": "wrong"})
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_refresh_token():
    async with AsyncClient(app=app, base_url="http://test") as client:
        login = await client.post("/auth/login", data={"username": "test@example.com", "password": "secret123"})
        refresh = await client.post("/auth/refresh", json={"refresh_token": login.json()["refresh_token"]})
        assert refresh.status_code == 200 and "access_token" in refresh.json()
