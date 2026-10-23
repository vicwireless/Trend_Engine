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
| Day 21 | 2+ samples passed; first POD listings live with partner attached; personalized test order rendered correctly | enable personalized POD | keep digital-only |
| Day 45 | Any niche with ≥ 10 orders or contribution/100 visits above $15 | shift 50% of new concepts to it; start bundle ladder | broaden candidates; no new spend |
| Day 90 | Operating result positive 2 consecutive weeks; owner time ≤ 2 h/week; no unresolved policy issues | release ROI-gated budget per SP-11 (EverBee API, Claude Max, ads to $10/day) | HOLD; 4 more cycles; if still negative, CONTRACT to digital-only lean stack |
| $8K trailing sales | Approaching the $10K Offsite Ads lock-in | reprice POD to absorb 12%; decide opt-in deliberately | — |
| Month 6 | Owner yield ≥ $150/hr for 8 weeks | consider Pinterest ads with a 30-day payback test | keep organic |
| Month 12 | Repeatability across ≥ 3 niches | evaluate TikTok Shop pipeline and productizing the engine | continue |

## Break-even (§4.6)

Lean stack ($51/mo): ≈ 5 orders/month ≈ 250 qualified visits at 2%. Growth stack ($195/mo):
≈ 18 orders/month ≈ 900 visits.

## Pause triggers (any one)

- Negative contribution after variable costs for 3 consecutive weeks
- IP complaint or policy notice
- Inability to fund committed Printify charges
- Executor publishing without a merged manifest (security breach)
- Hold backlog older than 24 hours
