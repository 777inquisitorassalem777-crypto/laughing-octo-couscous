# 🧠 Living NPC AI — v0.2

Persistent, social, memory-driven NPC architecture for games and simulations.

## v0.2 capabilities

- persistent worlds with PostgreSQL/pgvector
- Redis event bus + in-memory fallback
- optional FAISS local vector index
- OpenAI-compatible/Ollama LLM gateway
- WebSocket world-event streaming
- Unity SDK + autonomous world tick demo
- existing v0.1 domain interfaces preserved

## Run locally

```bash
python -m pip install -r requirements.txt
pytest -q
uvicorn app.api.app:app --reload
```

## Run the full infrastructure

```bash
docker compose up --build
```

## LLM

Copy `.env.example` to `.env` and configure `LLM_PROVIDER`, `LLM_BASE_URL`, `LLM_MODEL` and `OPENAI_API_KEY` as appropriate. Ollama can be used through its OpenAI-compatible `/v1` endpoint.

## API

- `GET /health`
- `POST /worlds`
- `GET /worlds/{world_id}`
- `POST /npcs`
- `GET /npcs/{npc_id}`
- `POST /npcs/{npc_id}/events`
- `POST /ticks`
- `POST /dialogue`
- `WS /ws/worlds/{world_id}`

See `docs/V0.2.md` and `sdk/unity/README.md`.
