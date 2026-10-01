from __future__ import annotations

import asyncio
import os
from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from app.core.multi_agent import MultiAgentDialogue
from app.core.runtime import World
from app.events.bus import build_event_bus
from app.llm.gateway import LLMGateway
from app.npc.agent import NPC
from app.npc.identity import Identity
from app.persistence.postgres import PostgresStore
from app.world.persistence import WorldPersistence

app = FastAPI(title="Living NPC Platform", version="0.2.0")
worlds: dict[str, World] = {}
event_bus = build_event_bus()
llm = LLMGateway()
store: PostgresStore | None = None
persistence: WorldPersistence | None = None


class WorldCreate(BaseModel):
    world_id: str = Field(min_length=1)

class NPCCreate(BaseModel):
    npc_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    archetype: str = "wanderer"
    values: dict[str, float] = {}

class EventIn(BaseModel):
    text: str

class DialogueIn(BaseModel):
    world_id: str
    npc_a: str
    npc_b: str
    topic: str


@app.on_event("startup")
async def startup():
    global store, persistence
    if os.getenv("POSTGRES_ENABLED", "false").lower() == "true":
        store = PostgresStore()
        await store.connect()
        persistence = WorldPersistence(store)

@app.on_event("shutdown")
async def shutdown():
    if store:
        await store.close()


def _world(world_id: str) -> World:
    if world_id not in worlds:
        worlds[world_id] = World(world_id, event_bus=event_bus, persistence=persistence)
    return worlds[world_id]

@app.get("/health")
def health():
    return {"status": "ok", "service": "living-npc-platform", "version": "0.2.0", "postgres": bool(store), "event_bus": type(event_bus).__name__}

@app.post("/worlds")
def create_world(data: WorldCreate):
    if data.world_id in worlds:
        raise HTTPException(409, "World already exists")
    worlds[data.world_id] = World(data.world_id, event_bus=event_bus, persistence=persistence)
    return {"world_id": data.world_id}

@app.post("/npcs")
def create_npc(data: NPCCreate):
    world = _world("default")
    if data.npc_id in world.npcs:
        raise HTTPException(409, "NPC already exists")
    npc = NPC(npc_id=data.npc_id, identity=Identity(name=data.name, archetype=data.archetype, values=data.values or {"care": 0.5, "truth": 0.5, "loyalty": 0.5}))
    world.add_npc(npc)
    return npc.to_public_dict()

@app.get("/npcs/{npc_id}")
def get_npc(npc_id: str):
    world = worlds.get("default")
    if not world or npc_id not in world.npcs:
        raise HTTPException(404, "NPC not found")
    return world.npcs[npc_id].to_public_dict()

@app.post("/npcs/{npc_id}/events")
async def npc_event(npc_id: str, event: EventIn):
    world = worlds.get("default")
    if not world or npc_id not in world.npcs:
        raise HTTPException(404, "NPC not found")
    npc = world.npcs[npc_id]
    npc.observe(event.text)
    await event_bus.publish(f"world:{world.world_id}", {"type": "npc.event", "world_id": world.world_id, "npc_id": npc_id, "text": event.text})
    if persistence:
        await persistence.save(world)
    return npc.to_public_dict()

@app.post("/ticks")
async def tick():
    return await _world("default").tick_once_async()

@app.post("/dialogue")
async def dialogue(data: DialogueIn):
    world = worlds.get(data.world_id)
    if not world:
        raise HTTPException(404, "World not found")
    a, b = world.npcs.get(data.npc_a), world.npcs.get(data.npc_b)
    if not a or not b:
        raise HTTPException(404, "NPC not found")
    result = await MultiAgentDialogue(llm).exchange(a, b, data.topic)
    await event_bus.publish(f"world:{world.world_id}", {"type": "dialogue.completed", "world_id": world.world_id, "dialogue": result})
    return {"dialogue": result}

@app.get("/worlds/{world_id}")
def world_state(world_id: str):
    world = worlds.get(world_id)
    if not world:
        raise HTTPException(404, "World not found")
    return {"world_id": world.world_id, "tick": world.tick, "npcs": [n.to_public_dict() for n in world.npcs.values()]}

@app.websocket("/ws/worlds/{world_id}")
async def world_stream(websocket: WebSocket, world_id: str):
    await websocket.accept()
    world = worlds.get(world_id)
    if not world:
        await websocket.send_json({"type": "error", "message": "World not found"})
        await websocket.close(code=1008)
        return
    try:
        async for event in event_bus.subscribe(f"world:{world_id}"):
            await websocket.send_json(event)
    except WebSocketDisconnect:
        return
    except asyncio.CancelledError:
        return
