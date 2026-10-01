from __future__ import annotations

from app.llm.base import LLMProvider
from app.npc.agent import NPC


class MultiAgentDialogue:
    def __init__(self, provider: LLMProvider) -> None:
        self.provider = provider

    async def exchange(self, a: NPC, b: NPC, topic: str) -> list[dict]:
        prompt_a = (
            f"You are {a.identity.name}. Values={a.identity.values}. "
            f"Emotion={a.emotion.__dict__}. Discuss: {topic}"
        )
        first = await self.provider.generate("Stay in character.", prompt_a)

        prompt_b = (
            f"You are {b.identity.name}. Values={b.identity.values}. "
            f"Emotion={b.emotion.__dict__}. Respond to this NPC statement:\n{first}"
        )
        second = await self.provider.generate("Stay in character.", prompt_b)

        a.remember(f"{b.identity.name} said: {second}", event_type="dialogue")
        b.remember(f"{a.identity.name} said: {first}", event_type="dialogue")

        return [
            {"speaker": a.npc_id, "text": first},
            {"speaker": b.npc_id, "text": second},
        ]
