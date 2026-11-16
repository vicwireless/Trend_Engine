# Incident 2026-11-16: Etsy write token revoked, seasonal release not published

**Impact.** No Etsy listing was changed. Release `2026-11-15-seasonal-verify` (one listing) stopped at the
Etsy token exchange, before any marketplace call. Ledger: `2026-11-15-seasonal-verify+0`, status `failed`.

**What happened.** 19:29:52 UTC, executor run 43939879292, after PR #32 was merged:
`Etsy token refresh -> 400 (invalid_grant: refresh_token is revoked)`.

**Cause.** Etsy issues a new refresh token every time one is used and revokes the old one. The executor
used the write token on 2026-10-23 and 2026-10-26 and never saved the new one back to the
`ETSY_WRITE_REFRESH_TOKEN` secret, so the secret has held a dead token since then. The metrics job had the
same fault on 2026-11-01 and was fixed in PR #24; the executor was not. `docs/metrics.md` already noted the gap.

**Reconciliation of the ledger line.** The line says `write_attempted: true` because, at the time, any
client error after the `pending` line was recorded that way. The error text shows the failure was the token
exchange; the Etsy API was never called. True outcome: nothing written. The line is left as it is (ledger
lines are never edited). The listing is re-released under a new manifest id, `2026-11-16-seasonal-games`,
so the old key is never re-run.

**Fixes (PR #34, merged).**
1. The executor workflow saves the rotated write token to the secret after every run.
2. A failed token exchange is now recorded as `write_attempted: false`, so the op can be retried.
3. Test: `test_revoked_write_token_fails_before_any_write_and_can_be_retried`.

**Still open.** A new write token needs an Etsy sign-in by the owner. Steps: top of
`reports/daily/2026-11-15-status.md`.
