from __future__ import annotations

import asyncio
import json
import os
from collections import defaultdict
from typing import Any, AsyncIterator, Awaitable, Callable

try:
    import redis.asyncio as redis
except ImportError:
    redis = None


Handler = Callable[[dict[str, Any]], Awaitable[None]]


class EventBus:
    async def publish(self, topic: str, event: dict[str, Any]) -> None:
        raise NotImplementedError

    async def subscribe(self, topic: str) -> AsyncIterator[dict[str, Any]]:
        raise NotImplementedError


class InMemoryEventBus(EventBus):
    def __init__(self) -> None:
        self._queues: dict[str, list[asyncio.Queue]] = defaultdict(list)

    async def publish(self, topic: str, event: dict[str, Any]) -> None:
        for queue in list(self._queues[topic]):
            await queue.put(dict(event))

    async def subscribe(self, topic: str) -> AsyncIterator[dict[str, Any]]:
        queue: asyncio.Queue = asyncio.Queue()
        self._queues[topic].append(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            if queue in self._queues[topic]:
                self._queues[topic].remove(queue)


class RedisEventBus(EventBus):
    def __init__(self, url: str | None = None) -> None:
        if redis is None:
            raise RuntimeError("redis package is not installed")
        self.url = url or os.getenv("REDIS_URL", "redis://localhost:6379/0")
        self.client = redis.from_url(self.url, decode_responses=True)

    async def publish(self, topic: str, event: dict[str, Any]) -> None:
        await self.client.publish(topic, json.dumps(event, ensure_ascii=False))

    async def subscribe(self, topic: str) -> AsyncIterator[dict[str, Any]]:
        pubsub = self.client.pubsub()
        await pubsub.subscribe(topic)
        try:
            async for message in pubsub.listen():
                if message.get("type") == "message":
                    yield json.loads(message["data"])
        finally:
            await pubsub.unsubscribe(topic)
            await pubsub.close()


def build_event_bus() -> EventBus:
    if os.getenv("REDIS_ENABLED", "false").lower() == "true":
        return RedisEventBus()
    return InMemoryEventBus()
