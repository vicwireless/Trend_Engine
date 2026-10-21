from src.executor import run as runner
from src.executor.approval import check

SHA = "abc123"
OWNERS = ["vicwireless"]


def pr(**kw):
    return {"number": 7, "merged_at": "2026-10-23T12:00:00Z", "merge_commit_sha": SHA,
            "base": {"ref": "main"}, "merged_by": {"login": "vicwireless"}, **kw}


def test_owner_merge_is_approval():
    record, errors = check([pr()], SHA, OWNERS)
    assert errors == [] and record == {"approver": "vicwireless", "pr": 7, "merge_sha": SHA}


def test_direct_push_is_not_approval():
    record, errors = check([], SHA, OWNERS)
    assert record is None and "direct pushes" in errors[0]


def test_merge_by_someone_else_is_refused():
    _, errors = check([pr(merged_by={"login": "mallory"})], SHA, OWNERS)
    assert "mallory" in errors[0]


def test_unmerged_or_other_base_is_refused():
    assert check([pr(merged_at=None)], SHA, OWNERS)[1]
    assert check([pr(base={"ref": "dev"})], SHA, OWNERS)[1]
    assert check([pr(merge_commit_sha="other")], SHA, OWNERS)[1]


def test_runner_refuses_writes_without_approval(monkeypatch, capsys):
    monkeypatch.setenv("GITHUB_ACTIONS", "true")
    monkeypatch.delenv("APPROVER", raising=False)
    monkeypatch.delenv("MERGE_SHA", raising=False)
    assert runner.main(["releases/whatever.yaml"]) == 2
    assert "APPROVER" in capsys.readouterr().err
