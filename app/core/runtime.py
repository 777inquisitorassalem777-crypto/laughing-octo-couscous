from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from typing import Any

from app.events.bus import EventBus, InMemoryEventBus
from app.npc.agent import NPC


@dataclass
class World:
    world_id: str
    npcs: dict[str, NPC] = field(default_factory=dict)
    tick: int = 0
    running: bool = False
    event_bus: EventBus = field(default_factory=InMemoryEventBus)
    persistence: Any = None

    def add_npc(self, npc: NPC) -> None:
        self.npcs[npc.npc_id] = npc

    async def _emit(self, event: dict) -> None:
        await self.event_bus.publish(f"world:{self.world_id}", event)

    def tick_once(self) -> dict:
        self.tick += 1
        for npc in self.npcs.values():
            npc.state.generation += 1
            npc.state.uncertainty = max(0.0, min(1.0, 0.8 * npc.state.uncertainty + 0.2 * (1 - npc.emotion.trust)))
            npc.state.stability = max(0.0, min(1.0, 1 - abs(npc.state.uncertainty - 0.5)))
            npc.state.clamp()
        return {"world_id": self.world_id, "tick": self.tick, "npcs": len(self.npcs), "timestamp": time.time()}

    async def tick_once_async(self) -> dict:
        event = self.tick_once()
        await self._emit({"type": "world.tick", **event})
        if self.persistence:
            await self.persistence.save(self)
        return event

    async def run(self, interval: float = 0.5) -> None:
        self.running = True
        while self.running:
            started = time.perf_counter()
            await self.tick_once_async()
            await asyncio.sleep(max(0.0, interval - (time.perf_counter() - started)))

    def stop(self) -> None:
        self.running = False
