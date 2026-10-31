# Pinterest Bulk Create CSVs

Made per release by `python -m tools.make_pin_csv` (the first 2026-11-02 schedule was withdrawn on 2026-11-03: Postiz already posts pins, so it would have duplicated them; pass `--skip` with posted images next time) from the dated `assets/pins/*/pins.md` files. Uploading is a
manual owner step (charter rule 1: nothing here posts to Pinterest).

## Upload steps (about 5 minutes)
1. Merge the PR first. Media URLs point at `raw.githubusercontent.com/.../main/`, so they only
   resolve after the images are on main. Spot-check one Media URL in a browser.
2. On Pinterest (desktop, business account): **Create > Create Pin > Bulk create Pins > Upload .csv**
   (wording varies; it sits next to the single-pin upload).
3. First time only: download Pinterest's template from that screen and confirm its headers match
   this file's (`Title, Media URL, Pinterest board, Thumbnail, Description, Link, Publish date, Keywords`).
   If they differ, tell Claude and the generator gets fixed.
4. Make sure every board in the file exists (create missing ones first; names must match exactly).
5. Test with a 3-row copy first. Pinterest has a reported bug that created only the first rows of
   a larger file. Then upload the full file and check **Scheduled Pins** shows every row.
6. Publish dates are written in UTC. If Pinterest shows them shifted, tell Claude and use `--slots`.

Optional: Share & Save links instead of plain listing URLs. Put `{"<listing_id>": "<share link>"}`
in a JSON file and pass `--links`. Pins already posted by hand: pass their image names to `--skip`.
