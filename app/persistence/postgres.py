from __future__ import annotations

import json
import os
from typing import Any

try:
    import asyncpg
except ImportError:  # optional until PostgreSQL is actually used
    asyncpg = None


SCHEMA = """
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS worlds (
    world_id TEXT PRIMARY KEY,
    tick BIGINT NOT NULL DEFAULT 0,
    state JSONB NOT NULL DEFAULT '{}'::jsonb,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE TABLE IF NOT EXISTS npcs (
    world_id TEXT NOT NULL REFERENCES worlds(world_id) ON DELETE CASCADE,
    npc_id TEXT NOT NULL,
    state JSONB NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY(world_id, npc_id)
);
CREATE TABLE IF NOT EXISTS memory_events (
    id BIGSERIAL PRIMARY KEY,
    world_id TEXT NOT NULL,
    npc_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    payload JSONB NOT NULL,
    embedding vector,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS memory_events_world_npc_idx ON memory_events(world_id, npc_id, id DESC);
"""


class PostgresStore:
    """Persistent world/memory adapter. The domain model remains independent of PostgreSQL."""

    def __init__(self, dsn: str | None = None) -> None:
        self.dsn = dsn or os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/livingnpc")
        self.pool = None

    async def connect(self) -> None:
        if asyncpg is None:
            raise RuntimeError("asyncpg is not installed; install requirements for PostgreSQL support")
        self.pool = await asyncpg.create_pool(self.dsn, min_size=1, max_size=10)
        async with self.pool.acquire() as conn:
            await conn.execute(SCHEMA)

    async def close(self) -> None:
        if self.pool:
            await self.pool.close()
            self.pool = None

    def _require(self):
        if self.pool is None:
            raise RuntimeError("PostgresStore is not connected")
        return self.pool

    async def save_world(self, world_id: str, tick: int, state: dict[str, Any]) -> None:
        pool = self._require()
        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO worlds(world_id,tick,state) VALUES($1,$2,$3::jsonb)
                ON CONFLICT(world_id) DO UPDATE SET tick=EXCLUDED.tick,state=EXCLUDED.state,updated_at=NOW()""",
                world_id, tick, json.dumps(state, ensure_ascii=False),
            )

    async def load_world(self, world_id: str) -> dict[str, Any] | None:
        pool = self._require()
        async with pool.acquire() as conn:
            row = await conn.fetchrow("SELECT world_id,tick,state FROM worlds WHERE world_id=$1", world_id)
        if not row:
            return None
        state = json.loads(row["state"]) if isinstance(row["state"], str) else dict(row["state"])
        return {"world_id": row["world_id"], "tick": row["tick"], "state": state}

    async def save_npc(self, world_id: str, npc_id: str, state: dict[str, Any]) -> None:
        pool = self._require()
        async with pool.acquire() as conn:
            await conn.execute(
                """INSERT INTO npcs(world_id,npc_id,state) VALUES($1,$2,$3::jsonb)
                ON CONFLICT(world_id,npc_id) DO UPDATE SET state=EXCLUDED.state,updated_at=NOW()""",
                world_id, npc_id, json.dumps(state, ensure_ascii=False),
            )

    async def load_npcs(self, world_id: str) -> list[dict[str, Any]]:
        pool = self._require()
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT npc_id,state FROM npcs WHERE world_id=$1 ORDER BY npc_id", world_id)
        return [{"npc_id": r["npc_id"], "state": json.loads(r["state"]) if isinstance(r["state"], str) else dict(r["state"])} for r in rows]

    async def append_memory(self, world_id: str, npc_id: str, event_type: str, payload: dict[str, Any], embedding: list[float] | None = None) -> None:
        pool = self._require()
        async with pool.acquire() as conn:
            if embedding:
                vector = "[" + ",".join(str(float(x)) for x in embedding) + "]"
                await conn.execute(
                    "INSERT INTO memory_events(world_id,npc_id,event_type,payload,embedding) VALUES($1,$2,$3,$4::jsonb,$5::vector)",
                    world_id, npc_id, event_type, json.dumps(payload, ensure_ascii=False), vector,
                )
            else:
                await conn.execute(
                    "INSERT INTO memory_events(world_id,npc_id,event_type,payload) VALUES($1,$2,$3,$4::jsonb)",
                    world_id, npc_id, event_type, json.dumps(payload, ensure_ascii=False),
                )

    async def recent_memory(self, world_id: str, npc_id: str, limit: int = 50) -> list[dict[str, Any]]:
        pool = self._require()
        async with pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT id,event_type,payload,created_at FROM memory_events WHERE world_id=$1 AND npc_id=$2 ORDER BY id DESC LIMIT $3",
                world_id, npc_id, limit,
            )
        return [dict(r) for r in rows]
