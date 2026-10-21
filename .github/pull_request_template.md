## Summary
<!-- What this PR changes or proposes, in 2–4 sentences. For a weekly release, this is the owner's brief. -->

## Release manifests
<!-- List releases/*.yaml added or changed, with op counts per type. "None" if code-only. -->

## Evidence
<!-- Signals and scores behind each new concept. Label estimates (EverBee/eRank/SerpApi) with source and date. Only Etsy Open API / Marketplace Insights numbers may be called "Etsy data". -->

## Compliance checklist
- [ ] No brands, teams, characters, celebrities, lyrics, attributed quotes, logos, or lookalikes; blocklist passes; any IP doubt was vetoed with a recorded reason
- [ ] Every AI-assisted asset and text is flagged `ai_assisted: true`, and every listing includes the AI disclosure attribute and sentence
- [ ] No buyer names, addresses, emails, or photos read or stored; personalization text only
- [ ] Demand figures are labelled by source; estimates are marked as estimates
- [ ] Prices meet the floor margin (digital 60%, POD 30% before ads) from cost snapshots ≤ 14 days old
- [ ] Ceilings respected: new listings/week, POD candidates/week, active niches, owner hours, ads cap, offsite ads
- [ ] Print QA passed for every print file (300 ppi, bleed, safe zone, contrast, sRGB, transparency, size)
- [ ] Titles ≤ 15 words, 13 specific tags, accurate attributes
- [ ] No secrets or `.env` files committed; no raw order exports committed
- [ ] Cohort decisions follow `docs/redefine.md` with the rule id cited; nothing retired on views alone
- [ ] POD only: production partner attached in Etsy for every new POD listing (Shop Manager); `partner_checked: true` set on each `printify_publish`
- [ ] Disclosure sentence and AI attribute spot-checked on 3 live listings
- [ ] Etsy Ads changes applied by hand per `ads.yaml` (≤ $3/day, ≤ 10 listings, ROAS ≥ 3 rule)
- [ ] Top 5 new keywords validated in Marketplace Insights (`data/insights/`)
- [ ] Shop Stats CSV exported to `data/stats_exports/`; session minutes appended to `data/time_log.csv`
- [ ] Holds in `data/orders/holds.json` resolved
- [ ] No open `ledger:` PR from the previous run
- [ ] CI is green, including the manifest dry-run

## Owner time
<!-- Estimated owner minutes for this review. -->
