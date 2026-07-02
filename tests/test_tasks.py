import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_create_and_list_tasks():
    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.post("/tasks/?project_id=1", json={"title": "Setup CI pipeline", "priority": "high"},
            headers={"Authorization": "Bearer <token>"})
        assert res.status_code == 201
        list_res = await client.get("/tasks/?project_id=1", headers={"Authorization": "Bearer <token>"})
        assert list_res.status_code == 200


@pytest.mark.asyncio
async def test_update_task_status():
    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.patch("/tasks/1", json={"status": "in_progress"},
            headers={"Authorization": "Bearer <token>"})
        assert res.status_code == 200 and res.json()["status"] == "in_progress"


@pytest.mark.asyncio
async def test_task_not_found():
    async with AsyncClient(app=app, base_url="http://test") as client:
        res = await client.get("/tasks/99999", headers={"Authorization": "Bearer <token>"})
        assert res.status_code == 404

# additional task tests
