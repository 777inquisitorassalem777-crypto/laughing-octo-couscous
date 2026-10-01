from fastapi.testclient import TestClient
from app.api.app import app, worlds

worlds.clear()
client = TestClient(app)
print(client.post('/worlds', json={'world_id': 'demo'}).json())
print(client.post('/npcs', json={'npc_id': 'alice', 'name': 'Alice', 'archetype': 'guardian'}).json())
print(client.post('/npcs/alice/events', json={'text': 'The player rescued me.'}).json())
print(client.post('/ticks').json())
