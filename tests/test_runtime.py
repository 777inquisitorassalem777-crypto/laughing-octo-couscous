from app.core.runtime import World
from app.npc.agent import NPC
from app.npc.identity import Identity


def test_world_tick():
    world = World("demo")
    world.add_npc(NPC("a", Identity("Alice")))
    result = world.tick_once()
    assert result["tick"] == 1
    assert result["npcs"] == 1
