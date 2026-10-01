from __future__ import annotations

import os
from app.llm.base import LLMProvider, MockLLM
from app.llm.openai_compatible import OpenAICompatibleProvider


class LLMGateway:
    """Provider-neutral gateway: OpenAI-compatible endpoints, Ollama, or mock."""
    def __init__(self, provider: LLMProvider | None = None) -> None:
        self.provider = provider or self._from_env()

    def _from_env(self) -> LLMProvider:
        kind = os.getenv("LLM_PROVIDER", "mock").lower()
        if kind in {"openai", "openai-compatible", "ollama"}:
            base = os.getenv("LLM_BASE_URL", "http://localhost:11434/v1" if kind == "ollama" else "https://api.openai.com/v1")
            model = os.getenv("LLM_MODEL", "llama3.2" if kind == "ollama" else "gpt-4o-mini")
            return OpenAICompatibleProvider(base, model, os.getenv("OPENAI_API_KEY"))
        return MockLLM()

    async def generate(self, system: str, user: str) -> str:
        return await self.provider.generate(system, user)
