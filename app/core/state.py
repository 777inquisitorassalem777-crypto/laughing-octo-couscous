from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class CoreState:
    generation: int = 0
    harmony: float = 0.5
    uncertainty: float = 0.5
    stability: float = 0.5
    spark_index: float = 0.0
    values: Dict[str, float] = field(default_factory=lambda: {
        "care": 0.5,
        "freedom": 0.5,
        "truth": 0.5,
        "loyalty": 0.5,
    })
    goals: List[str] = field(default_factory=list)

    def clamp(self) -> None:
        for name in ("harmony", "uncertainty", "stability", "spark_index"):
            setattr(self, name, max(0.0, min(1.0, getattr(self, name))))
        for key, value in self.values.items():
            self.values[key] = max(0.0, min(1.0, value))
