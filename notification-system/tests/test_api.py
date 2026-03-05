import pytest


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_create_task(client):
    resp = await client.post("/tasks", json={"title": "test task"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "test task"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_get_task(client):
    create = await client.post("/tasks", json={"title": "fetch me"})
    task_id = create.json()["id"]

    resp = await client.get(f"/tasks/{task_id}")
    assert resp.status_code == 200
    assert resp.json()["id"] == task_id


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    resp = await client.get("/tasks/00000000-0000-0000-0000-000000000000")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_list_tasks(client):
    await client.post("/tasks", json={"title": "a"})
    await client.post("/tasks", json={"title": "b"})
    resp = await client.get("/tasks")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 2


@pytest.mark.asyncio
async def test_create_task_with_payload(client):
    resp = await client.post(
        "/tasks", json={"title": "payload task", "payload": '{"key": "val"}'}
    )
    assert resp.status_code == 201
    assert resp.json()["payload"] == '{"key": "val"}'


@pytest.mark.asyncio
async def test_list_tasks_pagination(client):
    for i in range(5):
        await client.post("/tasks", json={"title": f"task {i}"})
    resp = await client.get("/tasks?limit=2&skip=0")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data["tasks"]) == 2
    assert data["total"] == 2
