# Weekly owner session (runbook)

Source: playbook v3.0 §9.1 (`docs/playbook-v3.0.md`). Target **60–90 minutes**; steady-state cap
`owner_hours_cap_per_week: 1.5`. The engine prepares one release PR (`release/week-NN`) before the
session. Merging it is the only approval and triggers the executor.

## Before the session (automated, no external writes)

| Task | When | Output |
|---|---|---|
| `sense` (SP-02) | daily 06:07 | `data/signals/YYYY-MM-DD/`, rolling `signals: week NN` PR (data only) |
| `measure` (SP-08) | daily 07:07 | `data/cohorts/`, `data/orders/`, `reports/daily/` |
| `order-guardian` (SP-09) | every 6 h | `data/orders/holds.json`; `red` GitHub issue on alert |
| `define-make` (SP-03→06) | Thu 03:07 | PR `release/week-NN` with `define.md`, `contact_sheet.md`, manifest, `pins.yaml`, `ads.yaml` |
| `weekly-close` (SP-10) | Fri 05:07 | `reports/weekly/NN/brief.md`, `decisions.yaml`, appended to the PR |
| `compliance-watch` (SP-12) | daily 08:07 | `reports/incidents/` |
| `monthly-gate` (SP-11) | 1st, 04:07 | `reports/monthly/` |

## The session

| Min | Step | Where |
|---|---|---|
| 0–10 | Read `brief.md`; note owner yield and the single most-off assumption | PR |
| 10–20 | Resolve holds in `holds.json`: release, message buyer (paste the drafted message in Etsy), or refund | Etsy, Printify |
| 20–35 | Review `define.md`: accept the niche set or edit weights in `docs/scoring.md` | PR |
| 35–55 | Skim `contact_sheet.md`; delete weak assets' lines from the manifest | PR |
| 55–65 | Validate the top 5 new keywords in Etsy Marketplace Insights; drop a screenshot or CSV in `data/insights/` | Shop Manager |
| 65–75 | Tick the PR checklist: partner attached on new POD listings, disclosure sentence spot-checked on 3 listings, ads changes applied per `ads.yaml` | Shop Manager |
| 75–80 | Export Shop Stats CSV to `data/stats_exports/`; append minutes to `data/time_log.csv` | Shop Manager, repo |
| 80–85 | Merge the release PR | GitHub |
| 85–90 | Watch the executor summary; merge the `ledger:` PR it opens; confirm no `red` issues | GitHub |

Removing an asset: delete its whole op group (create, uploads, activate, pins). Hashes are per op, but
`$ref:ops[N]` points by position, so deleting ops shifts later refs. Safer: comment on the PR and let
the engine regenerate the manifest; CI's dry-run must pass again before you merge.

## After merge

Only your merge counts as approval: the executor checks that the push is the merge commit of a PR
merged by a login in `approval.owner_logins` and writes `approver` and `merge_sha` on every ledger
line. Branch protection on `main`: require a pull request and the `test` check, **no required
review count** (GitHub blocks approving your own PRs).

- The executor writes `data/ledger/YYYY-MM-DD.jsonl` and opens a `ledger:` PR (data only). Merge it
  before the next release: the executor refuses to run while a ledger PR is open, because
  ceilings, cool-downs and idempotency read the ledger on `main`. If a run was refused for this
  reason, merge the ledger PR and use "Re-run jobs" on the executor workflow.
- Any failure writes `reports/incidents/` and stops the run. Reconcile by hand (check the channel,
  record the true outcome in the ledger), then re-run. Never delete ledger lines.

## Labor rule

If the session exceeds **2 hours for two consecutive weeks**, the monthly gate must propose a labor
fix (fewer concepts per week, stricter QA thresholds, or more automation) before any revenue
expansion (§9.1).

## Monthly and seasonal (§9.2)

- Monthly: SP-11 gate; rotate Etsy Ads spend; check the Offsite Ads position against $10K.
- Seasonal: launch collections 8–10 weeks before each peak in `data/calendar.yaml`; stop new
  seasonal POD listings once the provider's holiday cutoff is inside the processing window.
- Twice a year: paste new Etsy Seller Trend Report URLs into `data/trend_reports/queue.txt`.
