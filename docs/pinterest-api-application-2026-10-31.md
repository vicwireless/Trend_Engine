# Pinterest API access: application pack and fallback (2026-10-31)

## Summary
- **Apply now, but don't wait on it.** Pinterest approval runs in two stages: Trial, then Standard. Pins created under Trial are visible only to you, so automated posting that buyers see needs **Standard**, which needs a second review with a screen recording. Pinterest has a pinned notice acknowledging approval delays, and developers report 1 to 3+ weeks stuck in "Trial access pending". Realistic time to public automated posting: 3 to 6 weeks, and it can be denied.
- **Lowest-gate fallback: Pinterest's own free scheduler plus Bulk Create (CSV, up to 200 Pins per upload, with publish dates).** No API approval needed. The repo is public, so pin images in `assets/pins/` already have stable public URLs the CSV can point at. Claude can generate the CSV each release; Victor uploads it once (about 5 minutes) instead of posting pins one by one.
- **Paid fallback if CSV is flaky:** Tailwind (official Pinterest partner), about $18/mo annual or $30/mo monthly for ~150 posts/mo (third-party figures, verify on tailwindapp.com/pricing). Alura offers Etsy-listing-to-Pin automation. Neither is needed yet.
- **Cloud env:** every Pinterest host is DNS-blocked here. Allow `api.pinterest.com` (executor + OAuth token exchange), `developers.pinterest.com` (docs), and `community.pinterest.biz` (status threads).

Facts vs assumptions: tier structure and video requirement are from Pinterest's access-tiers doc as quoted in search results (I could not open the page directly; host blocked). Rate limits, review times and pricing are third-party or user reports, labeled as such.

## Step-by-step for Victor (about 15 minutes)

### 0. Prerequisites (check before you start)
1. Pinterest account for LMCGrows is a **Business account** (Settings > Account management > Convert to business, free).
2. **Claim the Etsy shop** on Pinterest: Settings > Claimed accounts > Etsy > Claim. This adds attribution and helps the app review look legitimate.
3. A **privacy policy URL**. Pinterest's app form asks for one. Use the draft at the bottom of this doc. Quickest hosting: paste it into the Etsy shop's About/Policies, or publish it as a GitHub Pages page / Google Doc set to "anyone with the link". Paste that URL in the form.

### 1. Create the app
1. Go to https://developers.pinterest.com/apps/ and log in **as the LMCGrows business account**.
2. Accept the developer terms if prompted, then click **Connect app** / **Create app**.
3. Fill the form with the text in "Form answers" below.
4. Submit. Status will show **Trial access pending**. Nothing else to do until it changes.

### 2. When status shows "Trial access" (approved)
1. Open the app, set **Redirect URI** to `http://localhost:8085/callback`.
2. Copy the **App ID** and click to reveal the **App secret**. Do NOT paste them into chat. Add them as cloud environment secrets `PINTEREST_APP_ID` and `PINTEREST_APP_SECRET` (same place `ETSY_SHOP_ID` lives).
3. Tell the thread "Pinterest trial approved". Claude will then: add `api.pinterest.com` check, build a one-time OAuth helper, run a read-only smoke test (list boards, account analytics), and draft the Standard-access screen recording script.

### 3. Standard access (second review)
1. Record a 1 to 2 minute screen capture: the Pinterest consent screen, approving the app, then the executor creating one Pin from a merged release file, then the Pin shown on the board.
2. In the app page click **Upgrade** / **Request Standard access**, attach the video, reuse the use-case text below.
3. Until Standard is granted, keep posting with the CSV fallback.

## Form answers (copy and paste)

**App name:** LMCGrows Pin Publisher

**Company name:** LMCGrows

**Company website:** https://www.etsy.com/shop/LMCGrows

**Privacy policy link:** (the URL from step 0.3)

**App description / What does your app do?**
> LMCGrows Pin Publisher is an internal, single-account tool for the LMCGrows Etsy shop, which sells original printable planners, wall art and print-on-demand designs. It publishes Pins for our own new product listings to our own boards and reads the analytics for those Pins so we can see which designs people save and click. Every Pin is reviewed and approved by the shop owner before it is published. The tool is not offered to other users and does not access anyone else's account.

**Use case / How will you use the Pinterest API?**
> We will (1) create Pins on our own boards that link to our own Etsy listings, at a modest pace of about 1 to 5 Pins per day, each one approved by the owner first; (2) read our own boards to choose the right board for each Pin; and (3) read analytics (impressions, saves, outbound clicks) for our own Pins and account weekly, to decide which designs to make more of. We do not scrape, follow, comment, message, or interact with other users' content, and we do not store any personal data about other Pinterest users. All images are our own original designs; images made with AI assistance are labeled as such in line with Pinterest's AI labeling.

**Primary use / category (if asked):** Content publishing; Analytics for own account.

**Platform:** Web / server (backend script).

**Expected users:** 1 (the shop owner's own account).

**Scopes requested (minimum needed):**

| Scope | Why |
|---|---|
| `user_accounts:read` | Read our own account and account-level analytics |
| `boards:read` | List our boards to pick the right one per Pin |
| `pins:read` | Read back created Pins and per-Pin analytics |
| `pins:write` | Create Pins for our own listings |
| `boards:write` | Optional: create a new seasonal board (e.g. "2027 Planners") |

Do not request ads, catalogs, or secret scopes. Smaller scope = easier review.

## How this fits the engine (no change to rails)
- The executor already has `pinterest_create_pin` (`src/executor/ops.py`) reading `PINTEREST_TOKEN`. Pins still go releases/*.yaml > PR > owner merge > executor. Nothing posts from a scheduled task.
- New after approval (not built yet): OAuth token helper with refresh (Pinterest access tokens are short-lived, refresh tokens long-lived; verify durations in docs), a read-only `pinterest_analytics` sense step writing `data/cohorts/`, and Pinterest added to the rate-limit/backoff client.
- Analytics before API: export Pinterest Analytics (Analytics > Overview > Export, CSV) weekly into `data/inbox/<date>/pinterest_analytics.csv`, like the eRank paste.

## Fallback options compared

| Option | Gate | Cost | Owner effort | Automation level | Verdict |
|---|---|---|---|---|---|
| Pinterest native Bulk Create CSV + scheduler | Business account only | $0 | ~5 min per batch upload | High: Claude makes the CSV, Pinterest schedules | **Use now** |
| Tailwind | Account signup | ~$18-30/mo (unverified) | Low | High; official partner; has CSV and Etsy flows | Use if CSV bugs bite |
| Alura (Etsy-focused) | Connect Etsy + Pinterest | Paid plan (verify) | Low | Auto-pins new listings | Backup; pins listing photos, not our tall pin art |
| Pinterest RSS auto-publish | Claimed website + business account | $0 | None after setup | Auto from feed | Etsy shop feed support unconfirmed; skip |
| Own API app (this pack) | Trial + Standard review | $0 | Video + secrets | Full, incl. analytics | Apply now, long lead time |

Known risk on CSV: a Pinterest community post (Oct 2026) reports only the first 2 rows of a 10-row CSV being created. Mitigation: download the official template from Pinterest's Bulk Create screen, test with 3 rows first, check Scheduled Pins after upload.

## Privacy policy draft (host anywhere public)

> **LMCGrows Pin Publisher: Privacy Policy** (effective 2026-10-31)
> LMCGrows Pin Publisher is an internal tool used only by the owner of the LMCGrows Etsy shop to publish Pins to the shop's own Pinterest account and read that account's analytics.
> **Data we access:** our own Pinterest account profile, boards, Pins and their analytics. **Data we do not access:** other users' profiles, messages, followers, or personal information.
> **Storage:** Pin IDs and aggregate analytics (impressions, saves, clicks) are stored in our private business records to measure product performance. Access tokens are stored as encrypted secrets and never shared.
> **Sharing:** we do not sell or share any data with third parties.
> **Deletion:** revoke access at any time in Pinterest Settings > Apps; contact us through our Etsy shop to request deletion of stored analytics.
> **Contact:** message LMCGrows via https://www.etsy.com/shop/LMCGrows

## Hosts to allow in the cloud environment
- `api.pinterest.com` (required: API calls, OAuth token exchange)
- `developers.pinterest.com` (docs, so Claude can verify scopes and limits)
- `community.pinterest.biz` (approval-status threads)
- Optional: `www.tailwindapp.com` if we go the Tailwind route

## Sources
- Pinterest access tiers doc (via search; host blocked): https://developers.pinterest.com/docs/key-concepts/access-tiers/
- Pinterest community, "Update: Developer App approvals" (delays acknowledged): https://community.pinterest.biz/t/update-developer-app-approvals/45527
- Trial pending reports: https://community.pinterest.biz/t/trial-access-pending-6-days-app-id-1600699-seeking-status-or-missing-requirements/50117
- Trial to Standard tips (n8n community): https://community.n8n.io/t/pinterest-api-trial-standard-any-success-stories-tips-for-standard-access-approval/257516
- Pinterest Bulk Create (official): https://create.pinterest.com/en-gb/product-features/bulk-content-creation/
- CSV row bug report (Oct 2026): https://community.pinterest.biz/t/bulk-create-pins-csv-only-creates-the-first-2-rows-reproduced-twice/51751
- CSV has no alt-text column: https://community.pinterest.biz/t/how-to-add-alt-text-in-pinterests-native-bulk-create-pins-csv/48058
- Tailwind pricing guide (verified 2026-06-10, third party): https://socialk.it/en/pricing/tailwind
- Tailwind review 2026: https://aisotools.com/blog/tailwind-app-review-2026
- Alura Etsy-to-Pinterest: https://www.alura.io/blog/how-to-automatically-post-etsy-listings-to-pinterest-and-skyrocket-your-traffic
- Rate limits (third party, unverified): https://www.upload-post.com/pinterest-api/
