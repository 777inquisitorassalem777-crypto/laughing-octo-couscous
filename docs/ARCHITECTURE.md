# Architecture

## Runtime

`World.tick_once()` is the deterministic simulation boundary. Production deployments can run
multiple worlds in isolated workers.

## NPC

An NPC is composed from:

- Identity
- CoreState
- EmotionState
- Relationships
- AppendOnlyMemory
- SemanticMemory

The public API exposes state without exposing internal implementation details.

## Memory

The MVP has an in-process append-only chain and a dependency-light semantic adapter.
The production persistence contract should be preserved when replacing these with PostgreSQL,
pgvector and FAISS.

## LLM

`LLMProvider` is an adapter interface. `MockLLM` makes tests deterministic.
`OpenAICompatibleProvider` supports OpenAI-compatible endpoints, including local gateways.

## Social simulation

Relationships and rumors are stateful. They can be expanded into a graph store without
changing NPC-facing interfaces.

## Metaphysical design layer

Pneuma, harmony, spark and related terminology are represented as conceptual metrics.
They are not claims that the software has consciousness or a soul.
