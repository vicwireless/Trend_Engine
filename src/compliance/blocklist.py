"""IP blocklist check. Any hit is a veto (CLAUDE.md rule 3)."""
from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import yaml

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "config" / "blocklist.yaml"


@dataclass(frozen=True)
class Hit:
    category: str
    rule: str
    match: str


class Blocklist:
    def __init__(self, data: dict):
        self._terms: list[tuple[str, str, re.Pattern]] = []
        for category, terms in (data.get("categories") or {}).items():
            for term in terms or []:
                pat = re.compile(r"(?<!\w)" + re.escape(str(term).lower()) + r"(?!\w)", re.IGNORECASE)
                self._terms.append((category, str(term), pat))
        self._regex: list[tuple[str, re.Pattern]] = []
        for entry in data.get("regex") or []:
            flags = 0 if entry.get("case_sensitive") else re.IGNORECASE
            self._regex.append((entry["name"], re.compile(entry["pattern"], flags)))

    @classmethod
    def load(cls, path: Path | str = DEFAULT_PATH) -> "Blocklist":
        with open(path, encoding="utf-8") as f:
            return cls(yaml.safe_load(f))

    def check(self, *texts: str | Iterable[str] | None) -> list[Hit]:
        hits: list[Hit] = []
        for text in _flatten(texts):
            for category, term, pat in self._terms:
                m = pat.search(text)
                if m:
                    hits.append(Hit(category, term, m.group(0)))
            for name, pat in self._regex:
                m = pat.search(text)
                if m:
                    hits.append(Hit("regex", name, m.group(0)))
        return hits


def _flatten(items) -> Iterable[str]:
    for item in items:
        if item is None:
            continue
        if isinstance(item, str):
            yield item
        else:
            yield from _flatten(item)
