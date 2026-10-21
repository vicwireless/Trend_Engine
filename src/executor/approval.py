"""Approval check (playbook SP-07, owner's rule of 2026-10-21: merge-only, no review count).

The executor runs only for a push to main that is the merge of a PR merged by the owner. GitHub
does not let the owner approve PRs opened under their own account, so the approval record is the
merge itself: merge commit SHA + merged_by + manifest hash, written to every ledger line.

Usage in the workflow:
    gh api repos/$REPO/commits/$SHA/pulls | python -m src.executor.approval $SHA
prints `approver=<login>` and `pr=<number>` for $GITHUB_OUTPUT, or exits 1 (fail closed).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]


def check(pulls: list[dict], merge_sha: str, owner_logins: list[str]) -> tuple[dict | None, list[str]]:
    merged = [p for p in pulls if p.get("merged_at") and p.get("merge_commit_sha") == merge_sha
              and (p.get("base") or {}).get("ref") == "main"]
    if not merged:
        return None, [f"{merge_sha} is not the merge commit of a PR into main; direct pushes are not approval"]
    pr = merged[0]
    who = (pr.get("merged_by") or {}).get("login")
    if who not in owner_logins:
        return None, [f"PR #{pr.get('number')} was merged by {who!r}, not an owner ({', '.join(owner_logins)})"]
    return {"approver": who, "pr": pr.get("number"), "merge_sha": merge_sha}, []


def main(argv: list[str] | None = None) -> int:
    argv = sys.argv[1:] if argv is None else argv
    sha = argv[0]
    config = yaml.safe_load((ROOT / "config" / "engine.yaml").read_text(encoding="utf-8"))
    owners = (config.get("approval") or {}).get("owner_logins") or []
    if not owners:
        print("approval.owner_logins is empty in config/engine.yaml", file=sys.stderr)
        return 1
    record, errors = check(json.load(sys.stdin), sha, owners)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print(f"approver={record['approver']}")
    print(f"pr={record['pr']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
