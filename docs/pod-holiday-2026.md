# Holiday POD test, 2026 (status: designs ready, release pending)

Six print-ready designs are in `assets/pod/masters/2026-11-16-holiday/` (transparent PNG, 300 ppi, sRGB,
all pass `src/qa/print_qa.py`; results in `print-qa.json` there). The release itself is **not** ready to
merge. `releases/pending/2026-11-16-pod-holiday.yaml` lists what is missing.

| Design | Product | Pixels |
|---|---|---|
| mug-christmas-icons | 11 oz mug, wrap | 2475 x 1155 |
| mug-merry-christmas | 11 oz mug, front and back | 2475 x 1155 |
| ornament-tree-2026 | Round ceramic ornament | 2000 x 2000 |
| ornament-snowflake | Round ceramic ornament | 2000 x 2000 |
| tee-christmas-bingo | Unisex tee, front | 4500 x 5400 |
| tee-happy-new-year-2027 | Unisex tee, front | 4500 x 5400 |

Pixel sizes are the commonly published print areas for these product types (assumption). They must be
checked against the chosen blueprint's placeholder before upload.

## What blocks it

| Blocker | Who | Detail |
|---|---|---|
| No Printify token, Printify hosts blocked from the engine's cloud session | Owner (token), owner (allow `api.printify.com` in the cloud environment's network settings) | Without the catalog the engine has no blueprint, provider or variant ids and no costs. Prices come only from dated cost snapshots (CLAUDE.md rule 6) |
| Etsy shop not connected in Printify | Owner | `printify_publish` requires `partner_checked: true` |
| No image-upload op in the executor | Engine | Add and test once a token exists |
| Tag lines not trademark-checked | Engine | "warm wishes, hot cocoa", "free space is for snacks" in classes 021 and 025 |

## Holiday cutoffs: not confirmed

Printify's 2026 cutoff table could not be read (printify.com blocked; web search on 2026-11-16 found no
official 2026 dates). What search did return, none of it verified: a peak-season surcharge of $0.40 per
US order through 2027-01-17 (Printify status page, via search snippet), and an older note that express
delivery extends the US Christmas cutoff to about 17 December. Standard cutoffs for mugs and ornaments
have historically fallen in the first half of December (assumption from prior years, not 2026 data).

**Recommendation.** POD for Christmas 2026 is only worth launching if the token and shop connection are
in place by about **27 November**. That leaves roughly a week of listing time before early-December
cutoffs, for new listings with no reviews. After that date, hold the Christmas designs, launch only the
New Year tee, and put the effort into the digital listings, which have no cutoff.
