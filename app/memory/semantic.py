from __future__ import annotations

import math
from typing import Iterable


class SemanticMemory:
    """Dependency-light semantic memory.

    Uses deterministic token overlap for the MVP. A FAISS adapter can replace
    this class without changing the NPC-facing interface.
    """

    def __init__(self) -> None:
        self._items: list[tuple[str, str]] = []

    def add(self, text: str, metadata: str = "") -> None:
        self._items.append((text, metadata))

    @staticmethod
    def _tokens(text: str) -> set[str]:
        return {x.strip(".,!?;:()[]{}").lower() for x in text.split() if x.strip()}

    def search(self, query: str, k: int = 5) -> list[dict]:
        q = self._tokens(query)
        scored = []
        for text, metadata in self._items:
            tokens = self._tokens(text)
            union = len(q | tokens) or 1
            score = len(q & tokens) / math.sqrt(union)
            scored.append({"text": text, "metadata": metadata, "score": score})
        return sorted(scored, key=lambda x: x["score"], reverse=True)[:k]
