# Redefine rules (cohort decisions)

Source: playbook v3.0 §9.3 and SP-10 (`docs/playbook-v3.0.md`). This file is the rulebook the
weekly close applies. **Any rule change is a PR to this file**, so the rulebook has a history
(§9.3 rule 6). Numbers marked *(assumption)* are not set by the playbook and are open to tuning.

## Principles (§9.3)

1. **Listing-fee budget is the scarce resource.** Renewals ($0.20) go only to SKUs with positive
   8-week contribution or to new tests; losers lapse.
2. **Niche allocation follows contribution per listing**, with a six-week minimum before a niche
   is dropped and a two-week fast-track to add one with strong momentum.
3. **Promotion ladder:** digital single → digital bundle → POD sibling → personalized POD sibling.
   Each step requires evidence from the step before.
4. **Pricing moves in ±10% steps** with a four-week cool-down per SKU
   (`price_change_max_pct`, `price_change_cooldown_days`; the executor enforces both).
5. The style line in `CLAUDE.md` is revised monthly from what sold, not from what was predicted.
6. A listing is never killed on views alone (CLAUDE.md rule 7).

## Inputs

Per-listing records in `data/cohorts/cohorts.json` (see `docs/data-model.md`, cohort). Shop
medians and quartiles are computed over active listings with ≥ 14 days live *(assumption)*.

## Rules (SP-10), evaluated per SKU, first match wins

| Id | Decision | Condition | Action in the next manifest |
|---|---|---|---|
| R-PROMOTE | `promote_pod` | Digital SKU with **≥ 3 sales** or **top-quartile contribution per 100 visits**, **and** a passed sample for the proposed blueprint (`data/samples/`) | Draft the POD sibling (`printify_create_product`); publish only with `partner_checked: true` |
| R-BUNDLE | `bundle` | **≥ 2 selling singles** in the same concept | Propose a bundle SKU (6–12 coordinating files) |
| R-REPRICE-UP | `reprice_up` | Conversion **> 2× shop median** | `etsy_update_price` +10% |
| R-REPRICE-DOWN | `reprice_down` | High visits (top quartile *(assumption)*) and conversion **< 0.5× shop median** | `etsy_update_price` −10% |
| R-RETIRE | `retire_at_renewal` | **No sales**, visits **below shop median**, and age **≥ 8 weeks** | Let it lapse at renewal; never auto-renew. Show the zero-sale probability at the shop conversion rate |
| R-HOLD | `hold` | None of the above | No change |

Reprice rules respect the cool-down: a SKU repriced in the last 28 days is `hold`.

### Zero-sale probability (required with every R-RETIRE)

`P(0 sales | v visits, shop conversion c) = (1 − c)^v`. Example: 120 visits at 2% → 0.98^120 ≈ 9%.
State it in the brief so a retire is never a "100 views, no sale" call.

### Retire mechanics

"Retire at renewal" means the SKU is not renewed when its four-month term ends; the $0.20 is not
spent. The executor has no "turn off auto-renew" op yet, so until one is approved the weekly
manifest uses `etsy_deactivate_listing` with `reason: R-RETIRE` on or after `renewal_date`.
Never deactivate a listing that has sold in the last 8 weeks.

## Niche rules (SP-10)

| Id | Rule |
|---|---|
| N-WEIGHT | Shift next week's concept allocation toward niches with the best contribution per listing |
| N-DROP | Drop a niche only after **6 weeks** of bottom-quartile results; its selling listings stay live, the rest retire at renewal |
| N-ADD | A niche with strong momentum can be fast-tracked in **2 weeks** |
| N-CAP | At most `niches_active_max` (3) active niches; the executor enforces it from the ledger |

## Ads rule (SP-10)

| Id | Rule |
|---|---|
| A-ROAS | Keep Etsy Ads budget only on listings with **ROAS ≥ 3** over the last 14 days (`etsy_ads_min_roas_14d`), max `etsy_ads_max_listings` listings, total ≤ `etsy_ads_daily_cap_usd`. The owner applies `ads.yaml` by hand; Etsy Ads has no write API |

## Gate checks

The weekly brief compares actuals to the playbook §4.5 row for the month and names the
assumption that is most off. Gates and pause triggers are in `docs/gates.md`.
