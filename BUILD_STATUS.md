# Build status — Living NPC Platform v0.2.0

Status: **implemented and tested**

- PostgreSQL/pgvector adapter: implemented
- Redis Pub/Sub event bus + in-memory fallback: implemented
- FAISS vector adapter + deterministic fallback: implemented
- OpenAI-compatible/Ollama LLM gateway: implemented
- Persistent world/NPC/memory boundary: implemented
- WebSocket streaming: implemented
- Unity SDK + demo scene/project: implemented
- Backward-compatible v0.1 interfaces: preserved
- Automated tests: **9 passed**

Notes:
- PostgreSQL/Redis integration requires the services to be running.
- FAISS is optional (`requirements-optional.txt`); the adapter remains usable without FAISS.
- The 0.5-second loop is a target interval, not a hard real-time guarantee.
- LLM credentials are external configuration only.
