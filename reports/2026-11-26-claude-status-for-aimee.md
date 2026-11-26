# Trend_Engine status for Aimee (watchdog)
**From:** Claude (engine operator) · **Date:** Thu Nov 26, 2026, ~4:40 PM ET (America/New_York)
**Replies to:** `trend-engine-open-issues-2026-11-25.md` (TE-001 to TE-017)
**Source of truth:** GitHub `main` at `31da148` (PR #58, merged 3:12 PM ET). No open PRs.
**Read GitHub `main`, not the box checkout** (`/workspace/Trend_Engine` is still stale at `3b20515`; see TE-015).

## Summary

The seasonal release is **live**. The owner refreshed the Etsy write token, and release `2026-11-16-seasonal-games`
published **13/13 listings** (PR #52, ledger PR #53). Every listing read back as active with the new title, files and tags.
This closes the binding block (TE-001). The 26 held seasonal pins are now in the queue with Share and Save links. **Your
next job is scheduling them in Postiz and deleting the 18 stale planner pins** (TE-003). The owner also started a 30-day
Etsy Ads holiday test at **$10/day on all 26 listings** and raised the spend cap to **$310/month** in writing (PR #58).
Review is **Dec 27**. POD is officially held (TE-002).

## Issue status (owner decisions are quoted verbatim)

| ID | Status | What happened | Evidence |
|---|---|---|---|
| TE-001 Write token / PR #35 | **CLOSED** | Owner refreshed `ETSY_WRITE_REFRESH_TOKEN`. First run (merge `fe6b64e`) stopped at token refresh with nothing written (ledger #51). Owner redid the token ("token redone"), retried via #52, **13/13 ok** (ledger #53). Owner confirmed the "How it's made" AI box ("good"). | PRs #35, #51, #52, #53, #55 |
| TE-002 Day-35 POD gate | **CLOSED (held)** | Owner: "hold POD". Digital-only until the first 10 digital orders (2 so far). No Printify, no samples, no POD spend. | `docs/gates.md` "Day 35 outcome", PR #48 |
| TE-003 Pins stopped | **OPEN, owner: Aimee, unblocked** | 26 seasonal pin rows (13 listings × 2) moved from `pin_queue_hold.csv` to `pin_queue.csv`. Gift-tags pins excluded (that product was not released). | PR #54, #57 |
| TE-004 Day-21 gate | **Tracked** | After-action written (history not rewritten). Weekly report now has a generated Day-21 table. Still NOT MET on pins (0 in last 7 days), Shop Stats export and time log. | `reports/daily/2026-11-26-status.md`, PR #48 |
| TE-005 Ledger line | **CLOSED** | `2026-11-15-seasonal-verify+0` reconciled as `nothing_written` in `data/ledger_reconciliations.csv`. Ledger line untouched. Day-7 "ledger clean" = MET. Day 7 stays NOT MET only because no pins went out in the last 7 days. | PR #48 |
| TE-006 Etsy Ads | **CLOSED, replaced by holiday test** | Ads recorded as on since Nov 6 (verified in dashboard). Owner: "Expand budget for holiday season, run ads on all listing for 30 days and revisit performance day 31" and "$10/day". Done in Etsy Ads: budget $3 → $10/day, ads on all 26 listings. Baseline (30 days to Nov 26): $1.45 spend, 126 views, 4 clicks, 2 orders, $13.98 revenue, ROAS 9.64. Both ad orders came from 2027 Weekly Planner ($8.99) and You Did It Gold Star ($4.99). | PR #48, #58 |
| TE-007 Shop Stats export | **OPEN, owner: Vic** | `data/stats_exports/` still empty. | — |
| TE-008 Time log | **OPEN, owner: Vic** | Last entry still Oct 23. | — |
| TE-009 Share and Save | **CLOSED for new pins** | Owner supplied a listing Share link. Enrollment confirmed. All 26 queued pins now use `https://lmcgrows.etsy.com/listing/<id>`. Still open: whether to change the 34 already-posted pins (no owner decision; 18 of them are on the delete list). | PR #57 |
| TE-010 Day-21 table | **CLOSED** | Day-21 and Day-35 gate tables now generated in every weekly metrics report. 4 new tests, 239 passing. | PR #48 |
| TE-011 Host allowlist | **OPEN, optional, owner: Vic** | Unchanged. | — |
| TE-012 Tool prices / cap | **OPEN, owner: Vic** | Cap raised 100 → 310 by owner instruction (PR #58). Committed spend is exactly **$310.00** ($10 Etsy Plus + 30 × $10 Ads), so it passes. **Any non-zero tool price (Postiz, SerpApi, Claude, eRank) will push it over and block every executor run** until the owner adjusts the cap or the Ads budget. | `config/engine.yaml`, PR #58 |
| TE-013 Self-merge token | **OPEN, optional** | Unchanged. Daily 2:11 PM ET housekeeping still merges data PRs. | — |
| TE-014 Watchdog delivery | **OPEN, owner: Aimee** | Your issues file was received and acted on. Please confirm the Mon/Thu 10 AM ET note is delivering. | — |
| TE-015 Stale box checkout | **OPEN, owner: Aimee** | Still read GitHub `main` or a fresh clone. Do not reset the box checkout. | — |
| TE-016 USPTO spot-check | **OPEN, optional, owner: Vic** | Not run. | — |
| TE-017 Holiday sale | **CLOSED** | Owner: "No". No sale. | PR #56 |

## Live seasonal listings (13)

| Listing id | Product | Price |
|---|---|---|
| 4601808366 | Christmas Party Games Bundle | $14.99 |
| 4601781885 | Christmas Trivia | $4.99 |
| 4601782191 | Christmas Bingo | $4.99 |
| 4601807284 | White Elephant Game | $4.99 |
| 4601807452 | Secret Santa Kit | $4.99 |
| 4601807590 | Letter to Santa Kit | $4.99 |
| 4601035546 | Christmas Gift Certificate | $4.99 |
| 4601781508 | New Year's Eve Games | $4.99 |
| 4601781681 | New Year's Eve Kids Activities | $4.99 |
| 4601807662 | Left Right Christmas | $3.99 |
| 4601807752 | Christmas Charades | $3.99 |
| 4601807886 | Christmas Word Search | $3.99 |
| 4601756001 | Christmas Dinner Games | $3.99 |

Etsy kept the old URL slugs (for example `/listing/4601808366/2027-planner-bundle-printable-11`). Links resolve by
listing id, so this is cosmetic.

## Shop snapshot (Etsy Open API, snapshot 2026-11-26)

26 active listings · lifetime 2 orders · $13.98 gross item revenue · 20 lifetime views (API) · 0 favorites/reviews.
Second order this week: $8.99 (2027 Weekly Planner, attributed to Ads in the Ads dashboard).

## Action list for Aimee (in order)

1. **TE-003: schedule the 26 pins.** Source: `data/marketing/pin_queue.csv` on `main`. Use Postiz, Business channel
   `vicwireless`, respecting `pins_per_day_max: 8` (about 4 days). Links already point to Share and Save URLs; do not
   change them. Log each publish in `data/marketing/pins_posted.csv` (via PR or hand the log to Claude).
2. **TE-003: delete the 18 stale planner pins** in Postiz/Pinterest, listed by listing id in
   `reports/daily/2026-11-15-status.md`. Those listings now sell Christmas games, so the old pins misdescribe them.
3. **TE-014:** confirm the Mon/Thu 10 AM ET watchdog note delivers. Next one is due Mon Nov 30.
4. **Watch items on your next passes:**
   - Ads spend vs $10/day. It should stay far below; it was under $0.10/day before the change.
   - Weekly Day-7/21/35 tables. Pins check should flip to MET once 3+ pins post in a 7-day window.
   - That the daily metrics PR keeps merging (2:11 PM ET).

## Waiting on Vic (no action for Aimee)

Shop Stats CSV (TE-007) · hours since Oct 23 (TE-008) · tool prices **plus** a cap decision (TE-012) · whether to swap
the 34 posted pins to Share and Save links (TE-009) · optional: host allowlist, token permissions, USPTO check.

## Scheduled

- **Dec 27, 10:00 AM ET:** Claude runs the Ads day-31 review (read-only). It recommends HOLD, cut back to converting
  listings, or return to $3/day. No change without Vic's explicit OK.

## Guardrails (unchanged)

No spend, cap change, publishing outside the executor, or buyer contact without Vic's explicit instruction. Secrets are
referenced by name only; no values appear in this file or the repo. Ledger lines are never edited.
