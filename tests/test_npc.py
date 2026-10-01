from app.npc.agent import NPC
from app.npc.identity import Identity


def test_npc_observation_changes_state():
    npc = NPC("n1", Identity("A", values={"care": 0.8}))
    before = npc.state.generation
    npc.observe("The player saved me.")
    assert npc.state.generation == before + 1
    assert len(npc.memory._entries) == 1
    assert 0 <= npc.state.spark_index <= 1


def test_relationship_clamped():
    npc = NPC("n1", Identity("A"))
    rel = npc.relationship("n2")
    rel.apply_event("betrayal", trust_delta=-10, resentment_delta=10)
    assert rel.trust == 0
    assert rel.resentment == 1
