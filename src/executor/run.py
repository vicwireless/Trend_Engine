"""Release executor.

    python -m src.executor.run releases/2026-10-27-wk44.yaml [...]
    python -m src.executor.run --dry-run releases/*.yaml     # preflight only, no writes

Runs only inside GitHub Actions (secrets come from Actions secrets, never from a .env file).
Per manifest: preflight every op (schema, payload_sha256, files, compliance, price floors,
ceilings); if anything fails, nothing is written. Then each op runs once, keyed by
manifest_id+op_index, with a pending/ok pair in data/ledger/. A replay skips ops already ok and
stops on any op whose earlier outcome is unknown.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import sys
from pathlib import Path

import yaml

from src.clients.base import ClientError, MissingCredential

from .ledger import Ledger, idempotency_key
from .ops import OPS, Context, OpDisabled, PreconditionFailed
from .validate import REF_RE, preflight

ROOT = Path(__file__).resolve().parents[2]


class ExecutorError(RuntimeError):
    pass


class PreflightFailed(ExecutorError):
    def __init__(self, errors: list[str]):
        super().__init__("preflight failed:\n  " + "\n  ".join(errors))
        self.errors = errors


class UnknownState(ExecutorError):
    pass


def load_config(root: Path) -> dict:
    return yaml.safe_load((root / "config" / "engine.yaml").read_text(encoding="utf-8"))


def resolve_refs(payload: dict, results: dict[int, dict]) -> dict:
    out = {}
    for k, v in payload.items():
        m = REF_RE.match(v) if isinstance(v, str) else None
        if m:
            idx, field = int(m.group(1)), m.group(2)
            if idx not in results or field not in results[idx]:
                raise UnknownState(f"cannot resolve {v}: op {idx} has no result {field!r}")
            v = results[idx][field]
        out[k] = v
    return out


def execute(manifest_path: Path, ctx: Context, ledger: Ledger, *, today: dt.date | None = None,
            dry_run: bool = False, approval: dict | None = None) -> dict:
    today = today or dt.datetime.now(dt.timezone.utc).date()
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    errors = preflight(manifest, manifest_path, ctx.root, ctx.config, ledger, today)
    if errors:
        raise PreflightFailed(errors)
    summary = {"manifest_id": manifest["manifest_id"], "dry_run": dry_run, "ops": []}
    if dry_run:
        summary["ops"] = [{"op_index": i, "op": op["op"], "status": "validated"} for i, op in enumerate(manifest["ops"])]
        return summary

    mid = manifest["manifest_id"]
    latest = ledger.latest()
    results = {e["op_index"]: e.get("result") or {} for e in latest.values()
               if e.get("manifest_id") == mid and e["status"] == "ok"}

    for i, op in enumerate(manifest["ops"]):
        key = idempotency_key(mid, i)
        prev = latest.get(key)
        base = {"manifest_id": mid, "op_index": i, "idempotency_key": key, "op": op["op"],
                "niche": op["niche"], "payload_sha256": op["payload_sha256"], **(approval or {})}
        if prev and prev["status"] == "ok":
            summary["ops"].append({**base, "status": "skipped_duplicate"})
            continue
        if prev and (prev["status"] in ("pending", "readback_failed") or prev.get("write_attempted")):
            raise UnknownState(f"{key} has status {prev['status']!r} from {prev['ts']}; reconcile by hand "
                               "before re-running (see reports/incidents/)")

        payload = resolve_refs(op["payload"], results)
        ledger.append({**base, "status": "pending", "write_attempted": True})
        try:
            out = OPS[op["op"]](payload, ctx)
        except (MissingCredential, OpDisabled, PreconditionFailed) as e:
            ledger.append({**base, "status": "failed", "write_attempted": False, "error": str(e)})
            raise ExecutorError(f"{key}: {e}") from e
        except (ClientError, OSError, KeyError, ValueError) as e:
            ledger.append({**base, "status": "failed", "write_attempted": True, "error": f"{type(e).__name__}: {e}"})
            raise ExecutorError(f"{key}: {e}") from e

        status = "ok" if out["readback_ok"] else "readback_failed"
        entry = ledger.append({**base, "status": status, "write_attempted": True,
                               "result": out["result"], "readback": out["readback"]})
        summary["ops"].append(entry)
        if status != "ok":
            raise UnknownState(f"{key}: read-back did not match the payload: {out['readback']}")
        results[i] = out["result"]
    return summary


def write_incident(root: Path, manifest_path: Path, error: Exception) -> Path:
    now = dt.datetime.now(dt.timezone.utc)
    path = root / "reports" / "incidents" / f"{now.date().isoformat()}-{manifest_path.stem}.md"
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(f"## {now.isoformat(timespec='seconds')} {type(error).__name__}\n\n"
                f"Manifest: `{manifest_path.as_posix()}`\n\n```\n{error}\n```\n\n")
    return path


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("manifests", nargs="*")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args(argv)

    if not args.dry_run and os.environ.get("GITHUB_ACTIONS") != "true":
        print("Refusing to write outside GitHub Actions. Use --dry-run locally.", file=sys.stderr)
        return 2

    approval = None
    if not args.dry_run:
        approval = {"approver": os.environ.get("APPROVER"), "merge_sha": os.environ.get("MERGE_SHA")}
        if not all(approval.values()):
            print("Refusing to write without APPROVER and MERGE_SHA from the approval step.", file=sys.stderr)
            return 2

    config = load_config(ROOT)
    ctx = Context(ROOT, config)
    ledger = Ledger(ROOT / "data" / "ledger")
    rc = 0
    for m in args.manifests:
        path = (ROOT / m) if not Path(m).is_absolute() else Path(m)
        try:
            summary = execute(path, ctx, ledger, dry_run=args.dry_run, approval=approval)
            print(json.dumps(summary, indent=2))
        except ExecutorError as e:
            rc = 1
            print(f"{m}: {e}", file=sys.stderr)
            if not args.dry_run:
                print(f"incident: {write_incident(ROOT, path, e)}", file=sys.stderr)
                break  # fail closed: stop the whole run
    return rc


if __name__ == "__main__":
    sys.exit(main())
