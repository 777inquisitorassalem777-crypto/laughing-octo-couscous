from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from typing import Any


class AppendOnlyMemory:
    """Tamper-evident in-process event chain.

    This is the MVP boundary. Replace storage with PostgreSQL while preserving
    the append/hash-chain contract.
    """

    def __init__(self) -> None:
        self._entries: list[dict[str, Any]] = []
        self._last_hash = "0" * 64

    def append(self, payload: dict[str, Any]) -> dict[str, Any]:
        entry = dict(payload)
        entry["timestamp"] = datetime.now(timezone.utc).isoformat()
        entry["_prev_hash"] = self._last_hash
        raw = json.dumps(entry, sort_keys=True, ensure_ascii=False).encode()
        entry["_hash"] = hashlib.sha256(raw).hexdigest()
        self._entries.append(entry)
        self._last_hash = entry["_hash"]
        return dict(entry)

    def recent(self, limit: int = 50) -> list[dict[str, Any]]:
        return [dict(x) for x in self._entries[-limit:]]

    def integrity_ok(self) -> bool:
        previous = "0" * 64
        for entry in self._entries:
            copy = dict(entry)
            stored = copy.pop("_hash")
            copy["_prev_hash"] = previous
            raw = json.dumps(copy, sort_keys=True, ensure_ascii=False).encode()
            if hashlib.sha256(raw).hexdigest() != stored:
                return False
            previous = stored
        return True
