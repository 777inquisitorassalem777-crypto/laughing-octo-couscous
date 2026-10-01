from __future__ import annotations

import math
from typing import Any

try:
    import faiss
    import numpy as np
except ImportError:
    faiss = None
    np = None


class FAISSVectorStore:
    """Optional local vector index with a deterministic lexical fallback."""

    def __init__(self, dimension: int = 384) -> None:
        self.dimension = dimension
        self.items: list[dict[str, Any]] = []
        self.index = faiss.IndexFlatIP(dimension) if faiss else None
        self.vectors = []

    def add(self, text: str, embedding: list[float], metadata: dict[str, Any] | None = None) -> None:
        if len(embedding) != self.dimension:
            raise ValueError(f"embedding dimension {len(embedding)} != {self.dimension}")
        item = {"text": text, "metadata": metadata or {}}
        self.items.append(item)
        self.vectors.append(embedding)
        if self.index is not None:
            arr = np.asarray([embedding], dtype="float32")
            faiss.normalize_L2(arr)
            self.index.add(arr)

    def search(self, embedding: list[float], k: int = 5) -> list[dict[str, Any]]:
        if not self.items:
            return []
        if self.index is not None:
            arr = np.asarray([embedding], dtype="float32")
            faiss.normalize_L2(arr)
            scores, ids = self.index.search(arr, min(k, len(self.items)))
            return [{**self.items[int(i)], "score": float(score)} for score, i in zip(scores[0], ids[0]) if i >= 0]
        def cosine(a, b):
            den = math.sqrt(sum(x*x for x in a)) * math.sqrt(sum(x*x for x in b)) or 1.0
            return sum(x*y for x,y in zip(a,b)) / den
        ranked = [(cosine(embedding, v), item) for v, item in zip(self.vectors, self.items)]
        return [{**item, "score": score} for score, item in sorted(ranked, reverse=True, key=lambda x: x[0])[:k]]
