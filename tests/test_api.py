from fastapi.testclient import TestClient
from app.api.app import app, worlds


def setup_function():
    worlds.clear()


def test_health():
    client = TestClient(app)
    assert client.get("/health").json()["status"] == "ok"


def test_create_npc_and_event():
    client = TestClient(app)
    response = client.post("/npcs", json={"npc_id": "a", "name": "Alice"})
    assert response.status_code == 200
    response = client.post("/npcs/a/events", json={"text": "Player helped me."})
    assert response.status_code == 200
    assert response.json()["memory_size"] == 1
