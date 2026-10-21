"""Dated cost snapshots in data/costs/ (CLAUDE.md rule 6)."""
from __future__ import annotations

import datetime as dt
import json
from pathlib import Path


class CostError(RuntimeError):
    pass


def load_snapshot(root: Path, rel_path: str, today: dt.date, max_age_days: int) -> dict:
    path = (root / rel_path).resolve()
    if not path.is_relative_to((root / "data" / "costs").resolve()):
        raise CostError(f"{rel_path} is outside data/costs/")
    if not path.exists():
        raise CostError(f"cost snapshot {rel_path} not found")
    snap = json.loads(path.read_text(encoding="utf-8"))
    age = (today - dt.date.fromisoformat(snap["as_of"])).days
    if age > max_age_days:
        raise CostError(f"{rel_path} is {age} days old (max {max_age_days}); re-fetch before pricing")
    if not snap.get("verified"):
        raise CostError(f"{rel_path} is not marked verified")
    return snap


def latest_channel_fees(root: Path, today: dt.date, max_age_days: int) -> dict:
    candidates = sorted((root / "data" / "costs").glob("*-channel-fees.json"))
    if not candidates:
        raise CostError("no channel fee snapshot in data/costs/")
    rel = candidates[-1].relative_to(root).as_posix()
    return load_snapshot(root, rel, today, max_age_days)["channels"]


def item_cost(snapshot: dict, key: str) -> float:
    items = snapshot.get("items") or {}
    if key not in items:
        raise CostError(f"cost key {key!r} not in snapshot")
    item = items[key]
    return float(item.get("unit_cost_usd", 0)) + float(item.get("shipping_usd", 0))
