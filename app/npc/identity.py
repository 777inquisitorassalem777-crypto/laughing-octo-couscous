from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Identity:
    name: str
    archetype: str = "wanderer"
    values: dict[str, float] = field(default_factory=dict)
    beliefs: dict[str, float] = field(default_factory=dict)
    fears: list[str] = field(default_factory=list)
    goals: list[str] = field(default_factory=list)

    def value(self, key: str) -> float:
        return self.values.get(key, 0.5)
