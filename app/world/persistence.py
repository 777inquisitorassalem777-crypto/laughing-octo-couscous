from __future__ import annotations

from typing import Any

from app.persistence.postgres import PostgresStore
from app.npc.agent import NPC


class WorldPersistence:
    def __init__(self, store: PostgresStore | None = None) -> None:
        self.store = store

    async def save(self, world) -> None:
        if not self.store:
            return
        await self.store.save_world(world.world_id, world.tick, {"running": world.running})
        for npc in world.npcs.values():
            await self.store.save_npc(world.world_id, npc.npc_id, npc.to_public_dict())
            for event in npc.memory.recent(1):
                await self.store.append_memory(world.world_id, npc.npc_id, event.get("type", "experience"), event)

    async def load_metadata(self, world_id: str) -> dict[str, Any] | None:
        if not self.store:
            return None
        return await self.store.load_world(world_id)
