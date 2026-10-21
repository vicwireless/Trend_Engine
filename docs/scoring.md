# Niche / offer score (scoring-v0.1)

> **Draft, not yet aligned with the playbook.** Playbook v3.0 SP-03 says weights live in this file
> but does not set them. It names **eight** inputs; this v0.1 implements five. Weights, ranges and
> bands below are assumptions to tune after the first 4 cohorts.

## Playbook SP-03 inputs vs this version

| SP-03 input | v0.1 coverage | Gap |
|---|---|---|
| `demand_momentum` (Trends slope + EverBee delta) | Demand **D** (SerpApi only) | EverBee delta not used |
| `competition_gap` (result count vs top-25 median favorites) | Openness **O** + Engagement **E** | Uses top 100, not top 25 |
| `gift_intent` (occasion words, "personalized" share) | — | Missing |
| `digital_fit` | — | Missing |
| `pod_fit` (blueprints, landed cost, margin at floor) | Price headroom **P** (partial) | Blueprint fit not scored |
| `seasonality` (weeks to next peak) | — | Missing; `data/calendar.yaml` now exists |
| `ip_risk` | Hard zero (veto before scoring) | Matches |
| `our_evidence` (cohort orders/visits) | — | Missing |
| — | Production fit **F** (owner minutes) | Not in SP-03; kept because it drives $/owner-hour |

scoring-v0.2 should add the four missing inputs. That needs the owner to pick weights.

The score ranks a niche + offer pair (e.g. "minimalist pickleball wall art, printable") from 0 to
100 so the weekly session spends owner time on the best few. It is a proxy for expected
**$/owner-hour**: demand you can catch, competition you can beat, margin you can keep, and work
you can afford.

## Inputs

| Input | Source | Label |
|---|---|---|
| `momentum` | SerpApi Google Trends, last 12 weeks vs prior 12 (`serpapi_trends.momentum`) | estimate |
| `interest` | SerpApi Google Trends, mean of last 12 weeks (0–100) | estimate |
| `active_listings` | Etsy `findAllListingsActive` count for the keyword | Etsy data |
| `median_favorites` | Median `num_favorers` of top 100 Etsy results | Etsy data |
| `median_price_usd` | Median USD price of top 100 Etsy results | Etsy data |
| `unit_cost_usd` | Dated cost snapshot in `data/costs/` (0 for most digital) | snapshot |
| `owner_minutes_per_listing` | Owner estimate for review + fixes per listing | owner |
| `sources` | Count of independent sources behind the inputs | — |
| `ip_veto` | Blocklist hit or IP review veto | — |

## Components (each 0–1)

| Component | Formula | Reads as |
|---|---|---|
| Demand **D** | `0.6 * clamp((momentum + 0.2) / 0.7) + 0.4 * interest / 100` | −20% momentum → 0, +50% → 1 |
| Openness **O** | `1 - clamp((log10(active_listings) - 2) / 3)` | ≤100 listings → 1, ≥100k → 0 |
| Engagement **E** | `clamp(log10(1 + median_favorites) / log10(501))` | 500+ favorites → 1 |
| Price headroom **P** | `clamp((margin_at_median - floor) / 0.30)` | margin at the market median price, above the floor in `config/engine.yaml` |
| Production fit **F** | `clamp(1 - (owner_minutes_per_listing - 2) / 28)` | 2 min → 1, 30 min → 0 |

`margin_at_median = (median_price - etsy_fees(median_price) - unit_cost) / median_price`, with fees
from the current Etsy fee snapshot in `data/costs/`.

## Score

```
score = 100 * K * (0.30*D + 0.20*O + 0.15*E + 0.20*P + 0.15*F)
K = 0.70 (1 source), 0.85 (2 sources), 1.00 (3+ sources)
```

Hard zeroes (fail closed): `ip_veto` is true, `margin_at_median` is below the floor, or any
required input is missing.

## Bands

| Score | Action |
|---|---|
| ≥ 65 | **Build**: full concept set, up to the weekly listing ceiling |
| 50–64.9 | **Test**: 3 listings max, one cohort |
| < 50 | **Park**: keep the signal, revisit in 4 weeks |

At most `niches_active_max` (3) niches are active at once; a new niche replaces the weakest
active one only through a cohort decision in `docs/redefine.md`.
