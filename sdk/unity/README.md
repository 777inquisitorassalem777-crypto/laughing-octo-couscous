# Living NPC Unity Demo v0.2

1. Start backend with `docker compose up --build`.
2. Create a world/NPC using the API or the demo script.
3. Create an empty Unity GameObject named `LivingNPCClient` and attach `LivingNpcClient`.
4. Attach `NpcController` to an NPC GameObject and assign the client.
5. Attach `WorldStreamDemo` to another GameObject to observe autonomous ticks.
6. Call `NpcController.Observe("Player rescued me")` from gameplay code.

The SDK uses the existing REST boundary and adds a polling demo. A production Unity transport can consume `/ws/worlds/{world_id}` with a WebSocket package without changing the backend domain model.
