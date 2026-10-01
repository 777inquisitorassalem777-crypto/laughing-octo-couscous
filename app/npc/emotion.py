from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EmotionState:
    valence: float = 0.0       # -1..1
    arousal: float = 0.2       # 0..1
    fear: float = 0.0
    anger: float = 0.0
    trust: float = 0.5
    sadness: float = 0.0

    def update(self, *, valence_delta: float = 0.0, fear_delta: float = 0.0,
               anger_delta: float = 0.0, trust_delta: float = 0.0) -> None:
        self.valence = max(-1.0, min(1.0, self.valence + valence_delta))
        self.fear = max(0.0, min(1.0, self.fear + fear_delta))
        self.anger = max(0.0, min(1.0, self.anger + anger_delta))
        self.trust = max(0.0, min(1.0, self.trust + trust_delta))
