"""Append-only execution ledger: data/ledger/YYYY-MM-DD.jsonl.

Each op writes a `pending` line before the external write and a final line after it. The pair
makes replays safe: `ok` means skip, `pending` without a final line or `failed` after a write
attempt means the outcome is unknown, so the executor stops (fail closed).
"""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path


def idempotency_key(manifest_id: str, op_index: int) -> str:
    return f"{manifest_id}+{op_index}"


class Ledger:
    def __init__(self, directory: str | Path, now=lambda: dt.datetime.now(dt.timezone.utc)):
        self.dir = Path(directory)
        self.now = now

    def entries(self) -> list[dict]:
        out = []
        for f in sorted(self.dir.glob("*.jsonl")):
            for line in f.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    out.append(json.loads(line))
        return out

    def latest(self) -> dict[str, dict]:
        """Last entry per idempotency key."""
        state: dict[str, dict] = {}
        for e in self.entries():
            state[e["idempotency_key"]] = e
        return state

    def append(self, entry: dict) -> dict:
        ts = self.now()
        entry = {"ts": ts.isoformat(timespec="seconds"), **entry}
        self.dir.mkdir(parents=True, exist_ok=True)
        with open(self.dir / f"{ts.date().isoformat()}.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, sort_keys=True) + "\n")
        return entry
