from __future__ import annotations

from abc import ABC, abstractmethod


class LLMProvider(ABC):
    @abstractmethod
    async def generate(self, system: str, user: str) -> str:
        raise NotImplementedError


class MockLLM(LLMProvider):
    async def generate(self, system: str, user: str) -> str:
        return f"[NPC] {user}"
