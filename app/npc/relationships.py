from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Relationship:
    target_id: str
    trust: float = 0.5
    respect: float = 0.5
    affection: float = 0.0
    fear: float = 0.0
    resentment: float = 0.0
    debt: float = 0.0
    history: list[str] = field(default_factory=list)

    def apply_event(self, event: str, *, trust_delta: float = 0.0,
                    affection_delta: float = 0.0, resentment_delta: float = 0.0,
                    debt_delta: float = 0.0) -> None:
        self.trust = max(0.0, min(1.0, self.trust + trust_delta))
        self.affection = max(-1.0, min(1.0, self.affection + affection_delta))
        self.resentment = max(0.0, min(1.0, self.resentment + resentment_delta))
        self.debt = max(-1.0, min(1.0, self.debt + debt_delta))
        self.history.append(event)
