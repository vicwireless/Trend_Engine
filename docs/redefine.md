# Cohort decision rules (redefine)

> **Draft standing in for playbook §9.3**, which was not in the repo when this was written.
> Thresholds are starting assumptions. Tune them after 4 cohorts have reached day 45.

A **cohort** is every listing launched in the same ISO week for the same niche. Decisions are
made per cohort, not per listing, so one quiet listing never drives a decision on its own.
A listing is never killed on views alone (CLAUDE.md rule 7).

## Checkpoints

Measure each cohort at **day 14, 30 and 45** after launch. Record a checkpoint in
`data/cohorts/<cohort_id>.json` with views (where Etsy returns them), favorites, orders, revenue,
and the data source. Rates are cohort totals: `fav_rate = favorites / views`,
`conv_rate = orders / views`. If views are unavailable, use only the order and favorite rules
and mark the decision `hold` unless an order rule fires.

## Rules (evaluated top to bottom; first match wins)

| Id | When | Condition | Decision | Action in the next manifest |
|---|---|---|---|---|
| R-SCALE | day ≥ 14 | orders ≥ 3 **and** conv_rate ≥ 2% | **scale** | Add 3–5 variants (sizes, colorways, bundles) in the same niche. Consider an Etsy Ads test within `etsy_ads_daily_cap_usd`. |
| R-PROMISING | day ≥ 14 | orders ≥ 1 **or** fav_rate ≥ 4% | **hold** | No change. Re-check at the next checkpoint. |
| R-TOO-EARLY | any | views < 150 and day < 30 | **hold** | Not enough exposure to judge. |
| R-REDEFINE-SEO | day ≥ 30 | views < 150 | **redefine** | Exposure problem: rewrite titles and all 13 tags from fresh signals, check taxonomy and attributes. Keep the designs. |
| R-ITERATE | day ≥ 30 | views ≥ 300, fav_rate ≥ 2%, orders = 0 | **iterate** | Interest without purchase: test price (−15%), first image, and mockup. One change per listing. `iterations += 1`. |
| R-REDEFINE-OFFER | day ≥ 30 | views ≥ 300, fav_rate < 2%, orders = 0 | **redefine** | Offer problem: new angle or format for the same buyer (e.g. printable → bundle, tee → mug). |
| R-RETIRE | day ≥ 45 | views ≥ 500, orders = 0, fav_rate < 1%, **iterations ≥ 1** | **retire** | Deactivate via `etsy_deactivate_listing` with `reason: R-RETIRE`. Frees a niche slot. |
| R-DEFAULT | — | none of the above | **hold** | |

## Niche slots

At most `niches_active_max` (3) niches are active. A new niche enters only when a cohort in an
existing niche reaches **retire**, or when the owner explicitly parks a niche in the weekly session.
The executor enforces the cap from the ledger (niches with writes in the last 28 days).

## Guardrails

- Never retire a cohort that has had zero iterations. Iterate or redefine first.
- Never retire on a single checkpoint with missing views; hold instead.
- Any decision other than hold is a line in the weekly PR brief with the rule id and the numbers
  that triggered it.
- Seasonal niches (e.g. holiday gifts) are judged against the season window, not the calendar
  day count. Mark them `seasonal: true` in the concept notes and hold outside the window.
