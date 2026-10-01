from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.core.state import CoreState
from app.memory.append_only import AppendOnlyMemory
from app.memory.semantic import SemanticMemory
from app.npc.emotion import EmotionState
from app.npc.identity import Identity
from app.npc.relationships import Relationship


@dataclass
class NPC:
    npc_id: str
    identity: Identity
    state: CoreState = field(default_factory=CoreState)
    emotion: EmotionState = field(default_factory=EmotionState)
    relationships: dict[str, Relationship] = field(default_factory=dict)
    memory: AppendOnlyMemory = field(default_factory=AppendOnlyMemory)
    semantic_memory: SemanticMemory = field(default_factory=SemanticMemory)

    def remember(self, text: str, *, event_type: str = "experience") -> None:
        self.memory.append({"type": event_type, "text": text})
        self.semantic_memory.add(text, event_type)

    def relationship(self, other_id: str) -> Relationship:
        if other_id not in self.relationships:
            self.relationships[other_id] = Relationship(target_id=other_id)
        return self.relationships[other_id]

    def observe(self, text: str) -> None:
        self.remember(text)
        self.state.generation += 1
        self.state.harmony = max(
            0.0, min(1.0, 0.85 * self.state.harmony + 0.15 * self.emotion.trust)
        )
        self.state.spark_index = max(
            0.0, min(1.0, 0.9 * self.state.spark_index + 0.1 * self.state.harmony)
        )
        self.state.clamp()

    def to_public_dict(self) -> dict[str, Any]:
        return {
            "npc_id": self.npc_id,
            "name": self.identity.name,
            "archetype": self.identity.archetype,
            "generation": self.state.generation,
            "emotion": self.emotion.__dict__,
            "state": self.state.__dict__,
            "relationships": {k: v.__dict__ for k, v in self.relationships.items()},
            "memory_size": len(self.memory._entries),
        }
