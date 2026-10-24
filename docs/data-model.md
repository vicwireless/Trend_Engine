# Data model

The source of truth for every record the engine writes. `schemas/*.json` mirror this file
(JSON Schema draft 2020-12). If you change a field here, change the schema in the same PR;
`tests/test_schemas.py` checks that each documented field exists in its schema.

Aligned with playbook v3.0 §5.3 (`docs/playbook-v3.0.md`). Fields the playbook lists are all
present; extra fields are noted as additions.

Conventions: ids are lowercase slugs or external ids as strings; timestamps are ISO 8601 UTC;
money is USD as a decimal number; every record is a file under a dated path (CLAUDE.md rule 10).

## signal
One observation of demand or competition. Stored in `data/signals/YYYY-MM-DD/*.json`.

| Field | Type | Notes |
|---|---|---|
| `signal_id` | string | `sig-YYYYMMDD-<slug>` |
| `source` | enum | `etsy_open_api`, `etsy_marketplace_insights`, `everbee`, `erank`, `serpapi_google_trends`, `serpapi_google_autocomplete`, `serpapi_google_trends_trending_now`, `pinterest_trends`, `manual` |
| `is_estimate` | boolean | Must be `true` for anything not from Etsy Marketplace Insights or the Etsy Open API (rule 5) |
| `keyword` | string | Search phrase observed |
| `niche` | string | Niche slug |
| `metric` | string | e.g. `active_listing_count`, `median_favorites`, `median_price_usd`, `interest_index`, `momentum` |
| `value` | number | |
| `unit` | string | e.g. `count`, `usd`, `index_0_100`, `ratio` |
| `window_start`, `window_end` | date | Period the value covers |
| `fetched_at` | datetime | |
| `raw_ref` | string \| null | Path to the raw response, if kept |
| `notes` | string | Optional |
| `license` | string \| null | Terms the data was obtained under (playbook §5.3) |

## concept
An original offer idea derived from signals. `data/scores/YYYY-MM-DD/*.json`.

| Field | Type | Notes |
|---|---|---|
| `concept_id` | string | `con-YYYYMMDD-<slug>` |
| `niche` | string | |
| `working_title` | string | |
| `offer_type` | enum | `digital`, `pod` |
| `product_format` | string | e.g. `printable_wall_art`, `planner`, `tshirt`, `mug` |
| `target_buyer` | string | |
| `gift_occasion` | string \| null | |
| `differentiation` | string | Why this is original, not a copy |
| `signal_ids` | string[] | At least one |
| `score` | number 0–100 | From `src/scoring/score.py` |
| `score_version` | string | Scoring doc version |
| `ip_review` | object | `status` (`pass`/`veto`), `reasons[]`, `reviewed_at`, `checks[]` (one per IP-screen check: `check`, `result`, `evidence`, `checked_at`, `classes` for trademark). Built by `src/compliance/ip_review.py`; see `docs/ip-screen.md` |
| `status` | enum | `proposed`, `approved`, `vetoed`, `built`, `parked` |
| `ai_assisted` | boolean | |
| `created_at` | datetime | |

## asset
A file produced for a concept. Lives under `assets/{digital,pod,pins}/`.

| Field | Type | Notes |
|---|---|---|
| `asset_id` | string | |
| `concept_id` | string | |
| `kind` | enum | `master`, `print_file`, `mockup`, `digital_download`, `pin_image` |
| `path` | string | Repo-relative |
| `sha256` | string | Hex |
| `width_px`, `height_px` | integer | |
| `ppi` | integer | Target print density |
| `color_profile` | string \| null | e.g. `sRGB IEC61966-2.1` |
| `file_bytes` | integer | |
| `ai_assisted` | boolean | Rule 2 |
| `provenance_path` | string \| null | Prompt provenance JSON from `image_gen.py` |
| `qa` | object | `passed`, `report_path`, `checked_at` |
| `created_at` | datetime | |
| `licenses` | object[] | Optional. Font, mockup and texture licenses: `kind`, `name`, `license`, `record_path` (playbook §5.3, SP-04) |

## listing
A listing draft or live listing on any channel.

| Field | Type | Notes |
|---|---|---|
| `listing_id` | string | Internal id |
| `concept_id` | string | |
| `channel` | enum | `etsy`, `printify_etsy`, `payhip`, `pinterest` |
| `external_id` | string \| null | Set after the executor writes it |
| `offer_type` | enum | `digital`, `pod` |
| `title` | string | ≤15 words, ≤140 chars |
| `description` | string | Must contain the AI disclosure sentence when `ai_assisted` |
| `tags` | string[] | Exactly 13, each ≤20 chars |
| `price_usd` | number | |
| `taxonomy_id` | integer \| null | Etsy taxonomy |
| `ai_assisted` | boolean | |
| `ai_disclosure_included` | boolean | |
| `asset_ids` | string[] | |
| `state` | enum | `draft`, `active`, `inactive`, `expired`, `retired` |
| `cohort_id` | string \| null | |
| `created_at`, `updated_at` | datetime | |
| `sku` | string | Stable SKU shared by the digital and POD siblings' records |
| `cost_snapshot_id` | string \| null | Path of the `data/costs/` snapshot used to price it |
| `disclosure_checked` | boolean | AI disclosure attribute and sentence verified |
| `partner_checked` | boolean \| null | POD only: production partner attached in Etsy; null for digital |
| `version` | integer | Increments on every executor write |
| `published_at` | datetime \| null | |
| `sibling_skus` | string[] | Optional. Digital ↔ POD cross-links (SP-05) |

## cohort
One listing's running performance record, per playbook §5.3 and SP-08 step 4. Niche-level views
are aggregated from these in the weekly close. `data/cohorts/cohorts.json` (array).

| Field | Type | Notes |
|---|---|---|
| `cohort_id` | string | `coh-<listing_id>` |
| `listing_id` | string | |
| `sku` | string | |
| `niche` | string | |
| `week_launched` | string | `YYYY-Www` |
| `offer_type` | enum | `digital`, `pod` |
| `visits` | integer | Cumulative, from the API or the latest Shop Stats CSV |
| `orders` | integer | Cumulative |
| `revenue_usd` | number | |
| `fees_usd` | number | Itemized at actual rates, Offsite-attributed orders included |
| `pod_cost_usd` | number | 0 for digital |
| `ad_spend_usd` | number | From `ads.yaml` |
| `contribution_usd` | number | Revenue − fees − POD cost − ad spend |
| `contribution_per_100_visits` | number \| null | |
| `days_live` | integer | |
| `renewal_date` | date \| null | Next $0.20 renewal (4 months or on sale) |
| `last_price_change_at` | date \| null | For the 28-day reprice cool-down |
| `stats_source` | string | `etsy_api` or the Shop Stats CSV path and date |
| `decision` | enum | `hold`, `promote_pod`, `bundle`, `reprice_up`, `reprice_down`, `retire_at_renewal` |
| `decision_rule` | string \| null | Rule id from `docs/redefine.md` |
| `decided_at` | datetime \| null | |

## order
A sale, stripped of buyer identity (rule 4). `data/orders/YYYY-MM/*.jsonl`.

| Field | Type | Notes |
|---|---|---|
| `order_id` | string | Channel receipt id |
| `channel` | enum | `etsy`, `payhip` |
| `created_at` | datetime | |
| `listing_id` | string \| null | Internal id if mapped |
| `external_listing_id` | string | |
| `quantity` | integer | |
| `item_price_usd` | number | |
| `shipping_usd` | number | |
| `discount_usd` | number | |
| `cogs_usd` | number \| null | From the cost snapshot used at sale time |
| `personalization_text` | string \| null | Text only, never photos |
| `cohort_id` | string \| null | |
| `is_digital` | boolean | Optional |
| `fees_usd` | number \| null | Optional. Where the API exposes them |
| `offsite_ads_attributed` | boolean \| null | Optional. If exposed |
| `flags` | string[] | Optional. Order-guardian hold reasons (SP-09) |
| `hold_state` | enum | Optional. `none`, `held`, `released`, `refunded`, `cancelled` |
| `supplier_order_id` | string \| null | Optional. Printify order id |
| `refund_usd` | number | Optional |

No name, address, email, or buyer user id field exists, and the schema forbids extra fields.

## release_manifest
A batch of proposed writes. `releases/YYYY-MM-DD-<slug>.yaml`. Merging the PR that adds it is
the owner's approval; the executor runs it.

| Field | Type | Notes |
|---|---|---|
| `manifest_id` | string | Matches the filename stem: `YYYY-MM-DD-<slug>` or the playbook's `week-YYYY-Www` |
| `created_at` | datetime | |
| `created_by` | string | |
| `summary` | string | One paragraph for the owner |
| `owner_minutes_estimate` | integer | Checked against `owner_hours_cap_per_week` |
| `week` | string | Optional. ISO week `YYYY-Www`; the playbook names files `releases/week-YYYY-Www.yaml`, and either name works as long as it matches `manifest_id` |
| `ads` | object | Optional declaration: `daily_budget_usd`, `offsite_ads_opted_in`. The executor never writes ads; it only checks the declaration against ceilings |
| `ops` | object[] | See below |

Each op: `op` (one of the allowlisted operations), `niche`, `payload` (validated against
`schemas/ops/<op>.json`), `payload_sha256` (SHA-256 of the canonical JSON of `payload`: sorted
keys, no whitespace, UTF-8). Payload strings of the form `$ref:ops[N].field` are resolved at run
time from the result of op N in the same manifest; the hash covers the unresolved payload.
Compute hashes with `python -m src.executor.hashing releases/<file>.yaml`.

The playbook also lists `approver` and `merge_sha` on the manifest. They do not exist until the PR
is merged, so the executor records them on every ledger line instead. Approval rule (owner decision,
2026-10-21): **merge-only, no review count**. The executor runs only for the merge commit of a PR
into `main` merged by a login in `approval.owner_logins` (`src/executor/approval.py`); a direct push
or anyone else's merge writes nothing.
