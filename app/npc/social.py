from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Rumor:
    subject_id: str
    source_id: str
    text: str
    credibility: float = 0.5
    repetitions: int = 1


@dataclass
class SocialGraph:
    rumors: list[Rumor] = field(default_factory=list)
    reputation: dict[str, float] = field(default_factory=dict)

    def spread(self, rumor: Rumor) -> None:
        for existing in self.rumors:
            if existing.subject_id == rumor.subject_id and existing.text == rumor.text:
                existing.repetitions += 1
                existing.credibility = min(1.0, existing.credibility + 0.03)
                return
        self.rumors.append(rumor)

    def reputation_of(self, npc_id: str) -> float:
        return self.reputation.get(npc_id, 0.5)

    def adjust_reputation(self, npc_id: str, delta: float) -> float:
        value = max(0.0, min(1.0, self.reputation_of(npc_id) + delta))
        self.reputation[npc_id] = value
        return value
