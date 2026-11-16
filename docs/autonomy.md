# Autonomy mode (owner directive, 2026-11-15)

On 15 Nov 2026 the owner gave a standing directive that replaces the charter's "the engine proposes,
the owner merges" rule:

> No more delays, checkpoints or approvals involving the owner. Owner approval is needed only when
> total committed spend would exceed $100/month. Zero inventory, low COGS, high ROI; POD and
> direct-to-consumer digital items only. Identify blockers objectively, use alternative approaches,
> and ask the owner only for what is truly unavoidable.

## What changed

| Before | Now |
|---|---|
| Owner merges every release PR | The engine merges its own PRs once the `test` check is green |
| Owner merges `ledger:` and `metrics:` PRs | The workflows try to merge them; an engine session merges any that are left |
| Owner ticks the AI field on every new draft | Existing active listings are replaced in place (`etsy_update_listing`), keeping the tick already set. New drafts still need the tick |
| No spend ceiling in code | `monthly_spend_commitment_cap_usd: 100`, enforced in executor preflight |

## What did not change (the rails)

The executor still refuses a manifest on any of these, and the engine does not weaken them to go faster:

- IP veto and `config/blocklist.yaml` (CLAUDE.md rule 3); uncertainty is a veto.
- The AI-disclosure sentence in every AI-assisted description (rule 2).
- No buyer names, addresses, emails or photos read or stored (rule 4).
- Cost snapshots no older than 14 days and the margin floors (rule 6).
- Ledger integrity: pending/ok pairs, idempotency keys, no deleted lines, no run while a ledger PR
  is open, publishing only through `releases/*.yaml` merged by PR. Direct pushes never publish.
- Etsy demand labels (rule 5), cohort rules instead of views alone (rule 7), fail closed (rule 8),
  rate limits (rule 9).

## The spend cap

`src/executor/validate.py::committed_monthly_spend` adds up, for every manifest:

| Line | Source |
|---|---|
| Confirmed subscriptions | `data/spend/subscriptions.csv` rows with status `active...` and a `monthly_usd` |
| Etsy Ads | 30 x the manifest's `ads.daily_budget_usd`; or 30 x `etsy_ads_daily_cap_usd` once the Etsy Ads row is marked active |
| Listing fees | $0.20 x new listings in the trailing 30 days plus this manifest |
| Anything else | The manifest's `new_monthly_commitments_usd` |

If the total is above the cap, preflight fails and nothing is written. Only the owner can approve
more: the engine never raises `monthly_spend_commitment_cap_usd` itself, and a PR that raises it must
quote the owner's instruction. Subscriptions with no recorded amount (Postiz, SerpApi, Claude, eRank
on 2026-11-15) are not counted; the daily status report names them until the owner records them.

## Who merges

Engine sessions act on GitHub under the owner's login, so `approval.owner_logins` stays
`[vicwireless]` and the ledger's `approver` field records that login. It now means "merged through
the PR path with CI green", not "a human reviewed it". If a future session runs under a different
login, add that login to `approval.owner_logins` in the same PR that needs it.

## What still needs the owner

Only what has no API: Etsy Ads on/off and budget, shop-wide sales, ticking the AI field on brand-new
drafts, connecting Etsy inside Printify, creating secrets and tokens, and any spend above the cap.
The daily status report (`reports/daily/`) lists these under "Only the owner can do this".

## Replacing a listing in place (`etsy_update_listing`)

Added 2026-11-15. Replaces an existing active digital listing's files, images, title, description,
tags and price while keeping its id, URL, state and editor-only fields. The owner's "With an AI
generator" tick is an editor-only field the API can neither read nor write, so it stays as set; the
new content must therefore also be AI-assisted and carry the disclosure sentence (preflight checks it).

Rails in preflight (`src/executor/validate.py`): blocklist, title length, disclosure sentence, margin
floor from a fresh cost snapshot, file hashes, at least 5 images, and **zero orders** for that listing
in a metrics snapshot no older than 3 days. A listing that has ever sold is never replaced in place, so
a buyer's purchase or review cannot end up attached to a different product. At run time the op refuses
a listing that is not active or not a download, never lets the listing reach zero files (Etsy would
turn it into a physical listing), and reads back title, price, state, tags, file names and images.
It counts against `max_new_listings_per_week`. No listing fee is charged for an edit.
