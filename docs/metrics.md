# Daily metrics (SP-08 "measure")

`.github/workflows/metrics.yml` runs daily at 07:07 UTC. It is read-only toward Etsy and writes only
to the `metrics/rolling` branch, which backs one open data-only PR titled `metrics: week of <Monday>`.
The owner merges it (weekly is enough); until then the job keeps adding days to the same PR.

| Output | What |
|---|---|
| `data/metrics/<date>.csv` | one row per listing: lifetime views, favorites, orders, units, item revenue, plus `_1d` deltas vs the previous snapshot |
| `data/metrics/<date>.shop.json` | shop totals, disclosure-sentence count, API quota left |
| `data/spend/etsy_ledger.csv` | Etsy fee and credit entries from the payment ledger (docs/spend-and-time.md) |
| `reports/weekly/<monday>-metrics.md` | week deltas, per-listing table, Day-7 gate status, verified spend, owner time, limits below. Also the PR body |

Run locally: `python -m src.metrics.collect && python -m src.metrics.weekly`.

## What the Etsy Open API v3 exposes (read-only probe 2026-10-31, shop 68737954)

| Need | Available? | Endpoint / note |
|---|---|---|
| Per-listing views | Lifetime total only | `views` on `shops/{id}/listings` and `listings/{id}`. Daily = delta between snapshots, so day 1 has no daily number |
| Per-listing favorites | Lifetime total only | `num_favorers` |
| Orders, units, revenue | Yes | `shops/{id}/receipts` (+ transactions). Needs `transactions_r`, which the READ token has and the write token does not |
| Shop totals | Yes | `shops/{id}`: active/digital listing count, sold count, favorers, reviews |
| Fees and payouts | Shop level | `shops/{id}/payment-account/ledger-entries`: fee and credit entries go to `data/spend/etsy_ledger.csv` daily (docs/spend-and-time.md) |
| Stats endpoints | No | `shops/{id}/stats`, `listings/{id}/stats` return 404 |
| Visits, traffic sources, search terms, conversion | No | Shop Stats only; export CSV to `data/stats_exports/` |
| Etsy Ads spend/clicks/ROAS | No | no Ads API |
| AI-generator field ticked in the editor | No | the job checks the disclosure SENTENCE in each description instead |
| Pins posted / pin clicks | No | no Pinterest token; Pinterest hosts are blocked in the cloud env. Pins are scheduled in Postiz (owner, 2026-10-31) or Bulk Create. Log each posted pin in `data/marketing/pins_posted.csv` (`date,pin,url`); it turns the gate check from UNVERIFIED into MET/NOT MET. A Postiz export or API read could fill it later (not built) |

Quota: 10 req/s and 10,000 req/day; a daily run uses about 5 requests.

## Rails

- Rule 1: no write tokens are given to the job; `ReadOnlySession` refuses any method but GET/HEAD.
- Rule 4: receipts go through `sanitize_receipt` and only per-listing aggregates are written.
- Rule 5: every number is labelled `etsy_open_api`.
- Rule 7: the summary never recommends a kill; cohort decisions stay in `docs/redefine.md`.
- Rule 8: a missing read token, 401/403, or exhausted 429 retries fail the run (GitHub emails the owner).

## Owner setup (once)

Etsy rotates the refresh token on every refresh and revokes a reused old one (both copies of the
read token were found revoked on 2026-11-01, about 18 hours after the job and cloud sessions had
each refreshed the same original). So every consumer needs its OWN token and must keep the newest one.

1. Run `python tools/etsy_oauth.py --mode read` once for GitHub and once more for the cloud env, so the
   two places hold different tokens (separate grants).
2. Actions secret `ETSY_REFRESH_TOKEN` = the GitHub token. Cloud env var `ETSY_REFRESH_TOKEN` = the other.
3. Actions secret `METRICS_SECRETS_PAT` = a fine-grained personal access token, repository
   `vicwireless/Trend_Engine` only, permission **Secrets: Read and write**, nothing else. The
   workflow's last step uses it to save the rotated token back to `ETSY_REFRESH_TOKEN` after each
   run. Without it the run fails loudly and the next run is revoked.

`ETSY_KEYSTRING`, `ETSY_SHARED_SECRET`, `ETSY_SHOP_ID` are already Actions secrets for the executor.
Each rotated token should carry a fresh 90-day life (unverified), so the GitHub copy should not
need re-minting. The cloud env copy cannot be saved back automatically; when a cloud session sees
`refresh_token is revoked`, re-mint it (step 1) or read the committed `data/metrics/` files instead.
The executor's `ETSY_WRITE_REFRESH_TOKEN` has the same rotation behavior and is not saved back yet.
