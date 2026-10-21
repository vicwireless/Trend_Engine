# Weekly owner session (runbook)

> **Draft standing in for playbook §9.1**, which was not in the repo when this was written.

Budget: **≤ 90 minutes of owner time per week** (`owner_hours_cap_per_week: 1.5`). The engine
prepares everything as one PR before the session; the owner reviews, edits, and merges. Merging is
the only approval. If the session would run over budget, cut scope, not checks.

## Before the session (automated, no external writes)

1. Refresh signals: Etsy search counts/prices/favorites, SerpApi Google Trends, EverBee
   (labelled as estimates). Write `data/signals/YYYY-MM-DD/`.
2. Refresh cost snapshots older than 14 days in `data/costs/` (Printify catalog + shipping,
   channel fees). Pricing stops if a snapshot is stale or unverified.
3. Score niches/offers (`src/scoring/score.py`) into `data/scores/YYYY-MM-DD/`.
4. Pull receipts (sanitized) and listing stats; update cohort checkpoints in `data/cohorts/`.
5. Apply `docs/redefine.md` rules and draft decisions.
6. Generate concepts, assets (with prompt provenance) and run print QA.
7. Draft `releases/YYYY-MM-DD-<slug>.yaml` with hashes (`python -m src.executor.hashing`).
8. Write `reports/weekly/YYYY-Www.md` and open one PR. The PR description is the owner's brief.
   CI dry-runs the manifest so ceilings and compliance are checked before the owner looks.

## The session (owner, ~75 min)

| Block | Minutes | What the owner does |
|---|---|---|
| Brief | 10 | Read the PR description: last week's numbers, cohort decisions, what is proposed and why. |
| Cohort decisions | 10 | Accept or change each non-hold decision. Check the rule id and numbers. |
| Concepts & IP | 20 | Veto anything with IP doubt (doubt = veto). Check differentiation. |
| Listings & assets | 25 | Spot-check titles, tags, prices vs floor, mockups, QA reports, AI disclosure. Edit in the PR. |
| Compliance checklist | 5 | Tick the PR template checklist. |
| Merge | 5 | Merge. The executor runs; check the ledger commit and any incident file. |

## After merge

- The executor writes `data/ledger/YYYY-MM-DD.jsonl` and commits it. Any failure writes
  `reports/incidents/` and stops the run.
- Incidents: resolve by hand (check the channel, record the true outcome in the ledger), then
  re-merge or re-run. Never delete ledger lines.
- Monthly: roll weekly reports into `reports/monthly/YYYY-MM.md` with $/owner-hour.

## Owner-hour log

Record actual minutes in the weekly report. Two weeks over budget in a row = cut
`max_new_listings_per_week` in `config/engine.yaml` by a third.
