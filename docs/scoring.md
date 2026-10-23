# Niche / offer score (scoring-v0.2)

Implements the eight inputs of playbook v3.0 SP-03. The playbook leaves the weights to this file;
the owner accepted the proposed defaults on 2026-10-22. Ranges and bands are assumptions to tune
after the first 4 cohorts. Changing a weight is a PR the owner merges.

The score ranks a niche + offer pair (e.g. "minimalist pickleball wall art, printable") from 0 to
100 so the weekly session spends owner time on the best few. It is a proxy for expected
**$/owner-hour**: demand you can catch, competition you can beat, margin you can keep, and work
you can afford.

## Weights

| SP-03 input | Weight | Component (0–1) |
|---|---|---|
| `demand_momentum` | 25 | `0.6 * clamp((momentum + 0.2) / 0.7) + 0.4 * interest / 100`; with an EverBee delta: `0.7 * that + 0.3 * clamp((everbee_delta + 0.2) / 0.7)` |
| `competition_gap` | 20 | `0.6 * openness + 0.4 * engagement` (below) |
| `gift_intent` | 10 | `clamp(gift_share / 0.5)`: half the top 25 titles with gift or occasion words → 1 |
| `digital_fit` | 10 | `clamp(digital_share / 0.6)`: 60% of the top 25 results are downloads → 1 |
| `pod_fit` / margin headroom | 10 | `clamp((margin_at_median - floor) / 0.30)`, times `clamp(pod_blueprints / 3)` for POD offers |
| `seasonality` | 10 | 1.0 at 8–10 weeks to the next peak in `data/calendar.yaml`; `weeks / 8` when closer; decays to 0.3 when further; evergreen = 0.5 |
| `our_evidence` | 10 | `0.5 * clamp(orders / 10) + 0.5 * clamp(contribution_per_100_visits / 15)` (the Day 45 gate in `docs/gates.md`) |
| production fit (owner minutes) | 5 | `clamp(1 - (owner_minutes_per_listing - 2) / 28)`: 2 min → 1, 30 min → 0 |
| `ip_risk` | veto | Hard zero before scoring |

`openness = 1 - clamp((log10(active_listings) - 2) / 3)` (≤100 listings → 1, ≥100k → 0).
`engagement = clamp(log10(1 + median_favorites) / log10(501))` (500+ favorites → 1).
`margin_at_median = (median_price - etsy_fees(median_price) - unit_cost) / median_price`, with fees
from the current snapshot in `data/costs/`.

`our_evidence` is 0 until a niche has sales, so a new niche tops out at 90. Proven niches pull ahead
as cohorts come in.

## Inputs

| Input | Source | Label |
|---|---|---|
| `momentum`, `interest` | SerpApi Google Trends, last 12 weeks vs prior 12, and mean (0–100) | estimate |
| `everbee_delta` | EverBee search-volume change (optional) | estimate |
| `active_listings` | Etsy `findAllListingsActive` count for the keyword | Etsy data |
| `median_favorites`, `median_price_usd` | Median `num_favorers` and USD price of the top 25 Etsy results | Etsy data |
| `gift_share` | Share of top 25 titles matching the gift/occasion word list (`score.gift_share`) | Etsy data |
| `digital_share` | Share of top 25 results with `listing_type` download or both (`score.digital_share`) | Etsy data |
| `pod_blueprints` | Matching Printify blueprints with an in-stock provider (POD offers only) | Printify |
| `weeks_to_peak` | `score.weeks_to_next_peak` over the niche's peaks in `data/calendar.yaml`; none = evergreen | calendar |
| `cohort_orders`, `cohort_contribution_per_100_visits` | `data/cohorts/` for the niche | our data |
| `unit_cost_usd` | Dated cost snapshot in `data/costs/` (0 for most digital) | snapshot |
| `owner_minutes_per_listing` | Owner estimate for review + fixes per listing | owner |
| `sources` | Count of independent sources behind the inputs | — |
| `ip_veto` | Blocklist hit or IP review veto | — |

## Score

```
score = 100 * K * Σ weight_i * component_i
K = 0.70 (1 source), 0.85 (2 sources), 1.00 (3+ sources)
```

Hard zeroes (fail closed): `ip_veto` is true, `margin_at_median` is below the floor, an unknown
`offer_type`, or any required input is missing (`pod_blueprints` is required for POD offers).

## Bands

| Score | Action |
|---|---|
| ≥ 65 | **Build**: full concept set, up to the weekly listing ceiling |
| 50–64.9 | **Test**: 3 listings max, one cohort |
| < 50 | **Park**: keep the signal, revisit in 4 weeks |

At most `niches_active_max` (3) niches are active at once; a new niche replaces the weakest
active one only through a cohort decision in `docs/redefine.md`.

## Changes from v0.1

- Added `gift_intent`, `digital_fit`, `seasonality` and `our_evidence`; EverBee delta now feeds demand.
- Openness and engagement merged into `competition_gap`; medians use the top 25 results, per SP-03.
- `pod_fit` scores Printify blueprint coverage for POD offers.
