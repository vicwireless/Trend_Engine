# Incident 2026-11-27: daily metrics job fails, Etsy answers 403 on receipts

**Impact.** No metrics snapshot for 27 Nov. Orders, revenue and views are not being recorded, so the daily
report cannot show whether the 13 seasonal listings published on 26 Nov are selling. Nothing on Etsy changed.
The live listings and the executor are not affected.

**What happened.** Metrics run 46041494361, 17:24 UTC: `GET shops/{id}/receipts -> 403`. The token refresh
itself worked and listing reads worked; only the receipts call was refused.

**Cause (inferred from the timeline, not confirmed by Etsy).** Etsy keeps one set of scopes per app and
user. On 26 Nov between 19:19 and 19:45 UTC the owner signed in again in "write" mode to replace the revoked
write token. That mode asked for `shops_r listings_r listings_w`, without `transactions_r`. The last good
metrics run was 17:39 UTC that day, before the sign-in; the first run after it failed. So the new sign-in
appears to have removed `transactions_r` from the existing read token.

**Fix in code (this PR).** Both sign-in modes now ask for the same scopes
(`shops_r listings_r listings_w transactions_r`), so the order of sign-ins no longer matters.

**Still needed from the owner (about 5 minutes).** The scopes only change when the owner signs in again:
1. Update the `Trend_Engine` folder on the computer used on 26 Nov (GitHub Desktop: Fetch origin, then Pull).
2. Run `python tools/etsy_oauth.py --mode read`, open the address, click Allow access, paste the address back.
3. Copy `refresh_token` from `.etsy_tokens_read.json` into the GitHub Actions secret `ETSY_REFRESH_TOKEN`.
4. Tell the engine. It re-runs the metrics job.

Not verified: whether this sign-in leaves the current write token working. It should, since the new grant
still includes `listings_w`. If the next release fails at token refresh, repeat with `--mode write` and the
secret `ETSY_WRITE_REFRESH_TOKEN`.

**Not changed.** The job still fails closed on 403 (CLAUDE.md rule 8). It was not altered to skip receipts.
