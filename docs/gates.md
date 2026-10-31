# Gates, KPIs and pause triggers

Source: playbook v3.0 §10 (`docs/playbook-v3.0.md`). The monthly gate (SP-11) evaluates these
against the last 4 weekly briefs and recommends exactly one of HOLD, EXPAND or CONTRACT.

## Objective

```
Owner yield ($/hr) = (monthly contribution after all variable costs − monthly fixed stack) ÷ monthly owner hours
```

Revenue may grow only when owner yield does not fall. Steady-state owner time ≤ 1.5 h/week, measured
from `data/time_log.csv`.

## KPIs (weekly)

Owner yield $/hr; operating result; contribution per 100 visits per SKU; shop conversion by source;
orders and AOV; digital vs POD mix; Pinterest click-through to Etsy and Payhip; Share & Save credits;
hold rate and resolution time; publish defect rate; API 429 count; cash available vs committed
Printify charges; Star Seller metrics (response rate, on-time shipping, rating).

## Gates

| Gate | Criteria | If met | If missed |
|---|---|---|---|
| Day 7 | ≥ 20 digital listings live with disclosures by 30 Oct 2026; executor ledger clean; pins posting (owner decision 2026-10-23; the playbook says ≥ 50 by day 7, and the clock starts at the first release publish, 23 Oct) | continue | fix pipeline before adding concepts |
| Day 21 (13 Nov 2026) — **re-scoped, proposal 2026-10-31; owner merge = approval** | Traffic and measurement: (1) ≥ 28 pins logged in `data/marketing/pins_posted.csv` (Postiz, Bulk Create or by hand), ≥ 3 in the last 7 days; (2) Etsy Ads running on the eligible listings (≤ 10, ≤ $3/day) from 5–9 Nov; (3) first Shop Stats export with visits by source in `data/stats_exports/`; (4) Share & Save and Offsite Ads state recorded in `data/spend/subscriptions.csv` notes or the weekly brief; (5) spend log and time log have an entry dated within 7 days | continue; start the POD sample order for Day 35 | no new listings until the missing check is fixed |
| Day 35 (27 Nov 2026) — POD, moved from Day 21 | Printify cost snapshot ≤ 14 days old in `data/costs/`; ≥ 2 physical samples passed (phrase-led sticker/mug/tee, owner-approved 2026-10-24); first POD listings live with production partner attached | keep POD in the weekly mix | keep digital-only; re-test after the first 10 digital orders |
| Deferred (after the first 10 POD orders) | Personalized test order rendered correctly (was a Day-21 criterion) | enable personalized POD | keep non-personalized POD |
| Day 45 | Any niche with ≥ 10 orders or contribution/100 visits above $15 | shift 50% of new concepts to it; start bundle ladder | broaden candidates; no new spend |
| Day 90 | Operating result positive 2 consecutive weeks; owner time ≤ 2 h/week; no unresolved policy issues | release ROI-gated budget per SP-11 (EverBee API, Claude Max, ads to $10/day) | HOLD; 4 more cycles; if still negative, CONTRACT to digital-only lean stack |
| $8K trailing sales | Approaching the $10K Offsite Ads lock-in | reprice POD to absorb 12%; decide opt-in deliberately | — |
| Month 6 | Owner yield ≥ $150/hr for 8 weeks | consider Pinterest ads with a 30-day payback test | keep organic |
| Month 12 | Repeatability across ≥ 3 niches | evaluate TikTok Shop pipeline and productizing the engine | continue |

### Why Day 21 was re-scoped (2026-10-31)

As of 31 Oct: 26 live digital listings, 6 lifetime views, 0 orders (Etsy data, `data/metrics/2026-10-31.csv`),
`data/samples/` empty and no Printify cost snapshot. The original Day-21 criteria (2 samples passed, POD live,
personalized order rendered) cannot be met by 13 Nov without spending on samples before there is any demand
signal, and they do not address the binding constraint, which is traffic. The re-scope keeps every original
criterion: the POD ones move to Day 35 and the personalized order is deferred, so nothing is silently skipped.
Alternative the owner can choose instead: keep Day 21 as written and order 2 samples by 3 Nov.

## Break-even (§4.6)

Lean stack ($51/mo): ≈ 5 orders/month ≈ 250 qualified visits at 2%. Growth stack ($195/mo):
≈ 18 orders/month ≈ 900 visits.

## Pause triggers (any one)

- Negative contribution after variable costs for 3 consecutive weeks
- IP complaint or policy notice
- Inability to fund committed Printify charges
- Executor publishing without a merged manifest (security breach)
- Hold backlog older than 24 hours
