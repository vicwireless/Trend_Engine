# Spend and owner time logs

Purpose: owner yield ($/hr) and burn need real numbers (docs/gates.md). Nothing in these files is
estimated. A tool with no confirmed amount is listed by name and left out of every total.

## Files

| File | Who writes it | What |
|---|---|---|
| `data/spend/etsy_ledger.csv` | metrics job, daily (`python -m src.metrics.spend`, GET only) | Every Etsy fee and credit from `shops/{id}/payment-account/ledger-entries`: listing fees, renewals, Etsy Plus, setup, transaction/processing fees, Etsy Ads and Offsite Ads fees once they occur. Sales, fee payments and payouts are left out. Unknown fee types are kept as `etsy_other` |
| `data/spend/manual.csv` | owner (`tools/log_entry.py spend`) | Spend outside Etsy: Claude, eRank, SerpApi, Postiz, samples, fonts. One row per charge, with the invoice or statement as `source` |
| `data/spend/subscriptions.csv` | owner (edit) | Register of recurring tools. `monthly_usd` stays blank until confirmed; only confirmed `active` rows count toward burn |
| `data/time_log.csv` | owner (`tools/log_entry.py time`) | Owner minutes per session (`date,session,minutes,notes`) |

The weekly report (`reports/weekly/<monday>-metrics.md`, also the rolling metrics PR body) prints a
"Spend (verified entries only)" section and an "Owner time (logged only)" section that turns
**Stale** when no time entry is dated within the last 7 days.

## Commands

```
python tools/log_entry.py time  --minutes 25 --session "ticked AI field + published 6 kidcore drafts" --date 2026-10-26
python tools/log_entry.py spend --vendor SerpApi --category tools --amount 25.00 \
    --description "Starter, 1 month" --recurring monthly --source "SerpApi invoice" --date 2026-10-24
```

Rails: no buyer data (rule 4); receipt ids are not stored in the spend log; the ledger read uses the
read-only session; amounts are USD as Etsy reports them.
