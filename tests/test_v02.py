import asyncio
from app.events.bus import InMemoryEventBus
from app.vector.faiss_store import FAISSVectorStore
from app.llm.gateway import LLMGateway


def test_event_bus_roundtrip():
    async def run():
        bus = InMemoryEventBus()
        received = []
        async def consume():
            async for item in bus.subscribe("x"):
                received.append(item)
                return
        task = asyncio.create_task(consume())
        await asyncio.sleep(0)
        await bus.publish("x", {"type": "tick", "n": 1})
        await asyncio.wait_for(task, timeout=1)
        assert received == [{"type": "tick", "n": 1}]
    asyncio.run(run())


def test_faiss_fallback_search():
    store = FAISSVectorStore(dimension=3)
    store.add("near", [1, 0, 0])
    store.add("far", [0, 1, 0])
    assert store.search([1, 0, 0], 1)[0]["text"] == "near"


def test_gateway_defaults_to_mock(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    async def run():
        return await LLMGateway().generate("system", "hello")
    assert "hello" in asyncio.run(run())
