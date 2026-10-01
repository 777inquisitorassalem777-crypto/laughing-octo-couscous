from app.memory.append_only import AppendOnlyMemory


def test_append_only_integrity():
    mem = AppendOnlyMemory()
    mem.append({"type": "event", "text": "hello"})
    mem.append({"type": "event", "text": "world"})
    assert mem.integrity_ok()
    assert len(mem.recent()) == 2
