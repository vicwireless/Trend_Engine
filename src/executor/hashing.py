"""Canonical payload hashing for release manifests.

    python -m src.executor.hashing releases/2026-10-27-wk44.yaml

prints the payload_sha256 for each op so the author can paste it in.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

import yaml


def canonical_json(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def payload_sha256(payload: dict) -> str:
    return hashlib.sha256(canonical_json(payload)).hexdigest()


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str]) -> int:
    for path in argv:
        manifest = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
        for i, op in enumerate(manifest.get("ops", [])):
            print(f"{path} ops[{i}] {op['op']}: {payload_sha256(op['payload'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
