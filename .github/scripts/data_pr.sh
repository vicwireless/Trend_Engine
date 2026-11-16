#!/usr/bin/env bash
# Push the current branch and get its data-only PR merged (autonomy mode, docs/autonomy.md).
#
#   data_pr.sh <branch> <title> <body-file>
#
# This repo's rule on main accepts the required 'test' check only from a pull_request run, and
# PRs or pushes made with the Actions token never start one (observed 2026-11-16: a dispatched
# check was green and the merge was still refused with 'Required status check "test" is expected').
# So:
#   1. If ENGINE_PAT can push and open PRs (a fine-grained token of the owner with Contents and
#      Pull requests write), push and open the PR with it. That starts CI; wait for it and merge.
#   2. Otherwise push with the Actions token and open NO pull request. An engine session opens
#      the PR under the owner's login (which starts CI) and merges it. A branch without a PR is
#      what tells the session, and the executor's guard, that data is waiting.
set -uo pipefail
branch="$1"; title="$2"; body="$3"
repo_url() { echo "https://x-access-token:$1@github.com/${GITHUB_REPOSITORY}.git"; }
sha=$(git rev-parse HEAD)

tok=""
if [ -n "${ENGINE_PAT:-}" ] && git push --force "$(repo_url "$ENGINE_PAT")" "HEAD:refs/heads/$branch" 2>/dev/null; then
  tok="$ENGINE_PAT"
else
  git push --force "$(repo_url "$ACTIONS_TOKEN")" "HEAD:refs/heads/$branch" || { echo "::error::could not push $branch"; exit 1; }
fi

n=$(GH_TOKEN="$ACTIONS_TOKEN" gh pr list --state open --head "$branch" --json number --jq '.[0].number // empty')
if [ -z "$tok" ]; then
  if [ -n "$n" ]; then GH_TOKEN="$ACTIONS_TOKEN" gh pr edit "$n" --title "$title" --body-file "$body" || true; fi
  echo "::warning::$branch pushed without an owner token, so no CI can start on it. An engine session must open or update its PR and merge it (docs/autonomy.md)."
  exit 0
fi

if [ -z "$n" ]; then
  GH_TOKEN="$tok" gh pr create --base main --head "$branch" --title "$title" --body-file "$body" \
    || { echo "::warning::owner token could push but not open a PR; left for an engine session"; exit 0; }
else
  GH_TOKEN="$tok" gh pr edit "$n" --title "$title" --body-file "$body" || true
fi

state=pending
for i in $(seq 1 36); do
  sleep 10
  state=$(GH_TOKEN="$ACTIONS_TOKEN" gh api "repos/${GITHUB_REPOSITORY}/commits/${sha}/check-runs" \
    --jq '[.check_runs[] | select(.name=="test")][0].conclusion // "pending"' 2>/dev/null || echo pending)
  if [ "$state" != "pending" ] && [ "$state" != "null" ]; then break; fi
done
if [ "$state" = "success" ]; then
  GH_TOKEN="$tok" gh pr merge "$branch" --squash --delete-branch \
    || echo "::warning::$branch is green but the merge was refused; an engine session must merge it"
else
  echo "::warning::test check on $branch is '$state'; PR left open"
fi
