# Trend-to-Revenue Engine: Etsy + Owned Channel Operating Playbook

**Version 3.0 | 21 October 2026 (US Eastern) | Supersedes "Etsy POD + Claude Code: Validated Operating Playbook v2.0"**

**Design brief (from owner):** A basic, fully automated system that follows online norms and trends to capture a revenue stream that is defined, marketed, measured and redefined every cycle, using the minimum owner man-hours per dollar derived. Etsy is the proving marketplace plus one additional channel. The system, not the owner, picks and rotates niches. Human involvement is one scheduled weekly review. Budget scales with speed-to-ROI; $1,500 is available on Day 0–1; anything recoverable inside 1–90 days may be funded into the thousands.

**Evidence notation (carried from v2.0):** **[V]** verified against a primary source dated on or before 21 Oct 2026. **[M]** modeled/illustrative. **[C]** conditional, must be confirmed in a live account. **[U]** not independently validated.

**What this is not:** an earnings guarantee, IP clearance, tax advice, or a security audit of third-party code. No Etsy, Printify, Pinterest or EverBee account was accessed.

---

## 0. How to use this document

1. Read §1–§4 once. They explain why v3.0 reorganizes the business around digital-first demand probes, why the "one channel" is Pinterest feeding an owned storefront, and how the money works.
2. Build with §7 (Day 0 to Day 21). Every step references a super prompt in §8.
3. Operate with §9. The weekly review runbook is the only recurring owner commitment.
4. The system redefines itself using the rules in §9.3 and the gates in §10. Those rules are the "perpetuity" mechanism.

---

## 1. Executive summary and what changed since v2.0

### 1.1 Decision

Run a **two-layer, digital-first catalog on one Etsy shop**, with **print-on-demand (POD) physical versions added only for designs that the digital layer has already proven**, distributed by an **automated Pinterest pipeline** that feeds both Etsy (earning the 4% Share & Save fee refund) and a **zero-fixed-cost owned storefront** (Payhip for digital, Printify Pop-Up Store for physical). The engine is a set of **Claude Code cloud scheduled tasks** that sense trends, define offers, manufacture assets, draft listings and marketing, read orders, and write a weekly decision brief. The only human action is **merging one pull request per week**, which is the approval record and the trigger for a deterministic publishing executor.

### 1.2 Why this beats the v2.0 plan on dollars per owner-hour

| Topic | v2.0 position | v3.0 change | Why it matters financially |
|---|---|---|---|
| Product core | Physical POD first (posters, mugs, blankets) in a fixed coastal niche | Digital downloads first; POD second; niche chosen by the engine | A digital sale carries Etsy's standard stack of $0.20 + 6.5% + 3% + $0.25 and nothing else: no production cost, no shipping, no reprint, no production-partner disclosure, no reserve-release dependency on tracking ([Feeproofed fee table](https://www.feeproofed.com/guides/etsy-fees-for-digital-downloads-2026/), [Etsy Fees Policy](https://www.etsy.com/legal/fees/)). It is the cheapest possible demand probe. |
| Automation level | Human gate per listing and per personalized order | One weekly PR merge; order exceptions auto-held, not auto-reviewed | Converts per-item approvals (minutes each) into one batch approval (60–90 min/week). |
| Approval control | Proposed bespoke approval service | GitHub branch protection + PR merge as the immutable approval record; GitHub Actions as the allowlisted executor | Same security property (agent cannot publish or spend; a human merge is required), built from free infrastructure. |
| Trend sensing | Manual Marketplace Insights lookups | Automated: Etsy Open API competition scans, EverBee Research API, SerpApi Google Trends, Etsy seasonal trend reports; manual Marketplace Insights only to validate finalists | Sensing runs daily without the owner. The EverBee Research API has documented auth and limits of 10 QPS and 50,000 queries/day ([EverBee developer guide](https://research-open-api.everbee.com/docs/research-open-api-guide.html)). |
| Second channel | Deferred to months 7–12 | Pinterest + owned storefront from Day 7 | Pinterest pins are made from the same image assets the design factory already produces; Share & Save refunds 4% of Etsy fees on orders driven by your own links ([Etsy Seller Handbook](https://www.etsy.com/seller-handbook/article/1503753198977)). |
| Compliance | AI disclosure "where appropriate" | AI disclosure is mandatory and enforced: Etsy began enforcement 14 January 2026; roughly 12,000 listings were removed and 8,500 warnings issued in Q1 2026 ([SellersNest](https://sellersnest.com/blog/etsy-ai-disclosure-rules/)) | Non-disclosure is now the top account-risk item; the executor refuses to publish any listing without the disclosure field set and the description line present. |
| Amazon Merch as alternative | Not evaluated | Rejected for now | From 1 June 2026 the default Creator tier pays $2.44 on a $19.99 tee, half the prior rate; higher tiers require 15–35% of sales from traffic you drive ([Merch Titans](https://merchtitans.com/blog/amazon-merch-royalty-changes-june-2026)). |
| TikTok Shop | Mentioned as later option | Rejected for Phase 1–2 | US referral fee rose from 6% to 8% on 4 August 2026 ([Hubfluence](https://www.hubfluence.io/tiktok-shop-seller-fees)), and the channel requires continuous short-video production, which is the most labor-intensive marketing format. |
| Shopify as owned store | Implicit later option | Rejected | The $5 Starter plan closed to new merchants around August 2026; Basic is $39/mo ([Webmedic](https://webmedic.com/shopify-starter-plan-guide), [Shopify pricing](https://www.shopify.com/pricing)). Payhip (free, 5% per sale) and Printify Pop-Up (no subscription or listing fees) cost nothing until a sale occurs ([Payhip pricing](https://payhip.com/pricing), [Printify Pop-Up](https://printify.com/pop-up-store/)). |
| Engine runtime | Local Windows machine, Claude Code CLI | Claude Code cloud scheduled tasks (Pro or Max plan) | Scheduled tasks run on Anthropic-managed infrastructure, continue when the laptop is closed, can use MCP connectors, and support hourly/daily/weekly schedules with a one-hour minimum interval ([Claude Code docs](https://code.claude.com/docs/en/routines)). |

### 1.3 Corrections retained from v2.0

All of v2.0's corrections remain valid and are embedded in the rails (§6): no 80–90% automation claim without measurement; no second writer per SKU; Printify personalization edited only in Printify; production partner confirmed inside Etsy; 100-views-no-sale is not a kill rule; funnel-based sensitivity instead of revenue forecasts; discover Etsy API quotas from headers; setup fee is whatever onboarding quotes.

---

## 2. The core concept: the Cycle Engine

### 2.1 Objective function

The business is optimized for one number:

```
Owner yield ($/hr) = (monthly contribution after all variable costs − monthly fixed stack) ÷ monthly owner hours
```

Everything else (listings, revenue, followers) is instrumentation. The engine is allowed to grow revenue only when owner yield does not fall. Owner hours are capped at **1.5 hours/week in steady state** (≈6.5 h/month), measured, not estimated.

### 2.2 The six-stage loop (runs weekly, with daily sub-tasks)

```
            ┌──────────── SENSE (daily) ────────────┐
            │ Etsy API competition scans            │
            │ EverBee keyword/listing analytics     │
            │ Google Trends (SerpApi) momentum      │
            │ Etsy seasonal trend reports           │
            │ Pinterest trend keywords (manual/3P)  │
            └───────────────┬───────────────────────┘
                            ▼
   ┌──────────── DEFINE (weekly) ────────────┐
   │ Score candidate niches & offers          │
   │ Pick ≤3 niches, ≤12 new concepts         │
   │ Decide digital-only vs digital+POD       │
   └───────────────┬──────────────────────────┘
                   ▼
   ┌──────────── MAKE (weekly) ──────────────┐
   │ Generate print masters + digital files   │
   │ QA pixels/bleed/contrast; IP screen      │
   │ Draft listings with disclosures & price  │
   │ Draft pins and link manifest             │
   └───────────────┬──────────────────────────┘
                   ▼
   ┌──── APPROVE (owner, once/week) ─────────┐
   │ Review PR: release manifest + contact    │
   │ sheet + KPI brief. Merge = approve.      │
   └───────────────┬──────────────────────────┘
                   ▼
   ┌──────────── MARKET (daily) ─────────────┐
   │ Executor publishes approved listings     │
   │ Pins scheduled; Share & Save links used  │
   │ Etsy Ads budget rules applied            │
   └───────────────┬──────────────────────────┘
                   ▼
   ┌──────────── MEASURE (daily/weekly) ─────┐
   │ Receipts, visits, conversion, fees       │
   │ Cohort contribution per listing          │
   │ Exceptions (orders, policy, API)         │
   └───────────────┬──────────────────────────┘
                   ▼
   ┌──────────── REDEFINE (weekly) ──────────┐
   │ Promote winners to POD / bundles         │
   │ Retire losers at renewal (no $0.20)      │
   │ Shift niche weights; update calendar     │
   └──────────────────────────────────────────┘
```

### 2.3 Why digital-first is the right probe

A digital listing costs $0.20 to publish and renews only when it sells or after four months ([Etsy Fees Policy](https://www.etsy.com/legal/fees/)). A physical POD listing costs the same $0.20 but every sale carries landed production cost, shipping variance, reprint risk, production-partner disclosure and reserve exposure. If the same artwork is listed first as a printable, the market reveals which designs and keywords attract buyers at near-zero marginal cost; only those designs are then promoted to POD where the dollar contribution per order is higher. The two layers also cross-sell: the digital listing links to the physical, and vice versa.

### 2.4 What "fully automated" means here, precisely

| Stage | Automated by engine | Owner |
|---|---|---|
| Sense | 100% | none |
| Define | 100% (proposals) | approves or edits via PR |
| Make | 100% (assets, QA, drafts) | spot-checks contact sheet |
| Approve | n/a | merges one PR |
| Market | 100% | none |
| Measure | 100% | reads one-page brief |
| Redefine | 100% (proposals) | approves via same PR |
| Order exceptions | auto-detected and auto-held | releases or refunds flagged orders in the weekly session (or sooner if alerted) |

Target: **≤90 minutes/week** after Day 21. Build phase: **20–30 owner hours** over three weeks [M].

---

## 3. Alternatives analysis: what materially changes the outlook

### 3.1 Channel and model matrix

Scoring: 5 = best. "Labor" is owner labor per $1,000 of monthly contribution once automated. Scores are judgments [M] grounded in the cited facts.

| Model / channel | Fee stack on a sale | Fixed cost | Margin | Labor | Platform risk | Automation fit | Verdict |
|---|---|---|---|---|---|---|---|
| **Etsy digital downloads** | $0.20 + 6.5% + 3% + $0.25 ([Feeproofed](https://www.feeproofed.com/guides/etsy-fees-for-digital-downloads-2026/)) | $0 | 5 | 5 | 3 (AI-disclosure enforcement; saturation) | 5 (Etsy API supports digital listings and file upload) [C] | **Core layer** |
| **Etsy POD via Printify/Printful** | Same stack + landed POD cost | $0 (Premium optional $39/mo or $299/yr, [Printify](https://printify.com/pricing/)) | 3 | 4 | 3 | 4 (Printify API, publish limit 200/30 min, [Printify rate limits](https://developers.printify.com/rate-limits)) | **Second layer for proven designs** |
| **Pinterest (traffic) → Etsy + owned store** | None on Pinterest; 4% Share & Save refund on Etsy orders you drive ([Etsy](https://www.etsy.com/seller-handbook/article/1503753198977)) | $0 with Pinterest API; Tailwind $17.99–29.99/mo as fallback ([Tailwind](https://support.tailwindapp.com/en/articles/17232111-tailwind-plans-and-pricing)) | n/a | 5 | 3 (algorithm; slow ramp) | 5 (pins are byproducts of design assets) | **The "one additional channel"** |
| **Payhip (owned digital store)** | 5% on free plan ([Payhip](https://payhip.com/pricing)) | $0 | 5 | 5 | 2 (no built-in traffic) | 4 | Owned-store endpoint for Pinterest traffic |
| **Printify Pop-Up Store (owned physical)** | None beyond base cost ([Printify](https://printify.com/pop-up-store/)) | $0 | 4 | 5 | 2 (no traffic) | 4 | Owned-store endpoint for POD |
| **TikTok Shop + POD** | 8% referral since 4 Aug 2026 + ~3% processing ([Hubfluence](https://www.hubfluence.io/tiktok-shop-seller-fees), [Marginory](https://marginory.com/data/tiktok-shop-fee-history)) | $0 | 3 | 1 (video) | 3 | 2 | Phase 3 option only with evidence |
| **Amazon Merch on Demand** | Royalty after 15% referral; Creator tier $2.44 on $19.99 tee since 1 Jun 2026 ([Merch Titans](https://merchtitans.com/blog/amazon-merch-royalty-changes-june-2026)) | $0 | 1 | 4 | 3 | 3 | Rejected |
| **Shopify Basic + Printify** | 2.9% + 30¢ processing | $39/mo ([Shopify](https://www.shopify.com/pricing)) | 4 | 3 | 2 | 4 | Rejected until owned-store traffic justifies a paid store |
| **Redbubble / TeePublic marketplaces** | Platform margins; fees up to ~50% of earnings reported ([WebSocial](https://websocial.ca/best-print-on-demand-sites-for-artists-2026/)) | $0 | 2 | 5 | 3 | 3 | Optional passive syndication later; low $/sale |

### 3.2 Value-adds that change long-term viability

1. **Digital-to-physical promotion ladder.** A design that sells as a $7–15 printable gets a $25–60 framed-print, mug, ornament or blanket version. This raises AOV without new creative work and spreads listing-fee budget to proven demand only.
2. **Bundles and collections.** Digital bundles (sets of 6–12 coordinating files) sell at higher price points with identical fees; Etsy's own fee table shows the effective fee rate falling from 18.5% at $5 to 11.8% at $20 ([Feeproofed](https://www.feeproofed.com/guides/etsy-fees-for-digital-downloads-2026/)). Bundling is the cheapest margin lever available.
3. **Own-traffic fee arbitrage.** Orders driven by Share & Save links refund 4% (6.5% for the first two weeks after enrollment) of the Etsy bill ([Etsy](https://www.etsy.com/seller-handbook/article/1503753198977)). Orders on Payhip pay 5% instead of ~9.5% + $0.45. Pinterest supplies both.
4. **Automated personalization without labor.** Printify's Etsy personalization syncs text and image layers to Etsy fields, renders a Live Preview for buyers, and imports buyer inputs into production; up to five personalization fields are allowed and placeholder text like "Your text here" is not allowed in images ([Printify](https://help.printify.com/hc/en-us/articles/40720228428433)). Personalized gifts are one of Etsy's strongest Fall/Winter 2026 signals (personalized friend gifts +1,400% searches) ([Etsy Trend Report](https://www.etsy.com/seller-handbook/article/1521255894814)).
5. **Seasonal calendar as code.** Etsy publishes dated trend reports with quantified search growth; the engine stores them as structured data and launches seasonal collections 8–10 weeks before each peak.
6. **Marketplace Insights via Etsy Plus.** Etsy Plus ($10/mo) includes unlimited Marketplace Insights searches, 15 listing credits and $5 Etsy Ads credit ([Etsy Fees Policy](https://www.etsy.com/legal/fees/), [Seller Handbook](https://www.etsy.com/seller-handbook/article/1404564905677)). That is the only official Etsy search-volume signal; the free tier allows 15 searches/week.
7. **Later: B2B software or templates.** The prompt library and executor are themselves sellable as a digital product. Not in Phase 1–2; noted for the 12-month gate.

### 3.3 Known headwinds the engine must respect

- **AI saturation and seller backlash.** Reporting in September 2026 describes long-time sellers leaving as AI-generated listings undercut human creators, with Etsy stating enforcement is complex at scale ([Digital Trends](https://www.digitaltrends.com/computing/etsy-sellers-are-quitting-as-ai-slop-floods-the-handmade-marketplace/)). Implication: the engine must produce differentiated, well-photographed, properly disclosed work and avoid the generic-template segment where price competition is worst.
- **Etsy's "Mark of the Maker" trend** (hand-painted +280%, hand-woven +230%) favors visible craftsmanship ([Etsy Trend Report](https://www.etsy.com/seller-handbook/article/1521255894814)). AI output should be styled toward textured, painterly, or typographic-craft aesthetics, not glossy renders.
- **Reserves and deposit timing.** New sellers' funds are generally eligible for deposit 14–20 days after a sale, and reserves release on tracking ([Etsy](https://help.etsy.com/hc/en-us/articles/360058722214-What-is-a-Payment-Account-Reserve), [Growtsy](https://www.growtsy.com/tools/etsy-deposit-checker)). Digital-first reduces exposure because there is no supplier charge to float.
- **Offsite Ads lock-in.** Once a shop exceeds $10,000 in trailing-365-day sales, 12% Offsite Ads participation becomes mandatory for life ([Etsy Help](https://help.etsy.com/hc/en-us/articles/360000338367-How-Etsy-s-Offsite-Ads-Work)). The pricing model must assume a share of orders at 12–15% once scale arrives.

---

## 4. Economics and ROI model

### 4.1 Fee stack (US seller, USD, Etsy Payments) [V]

```
Listing / renewal fee      $0.20 per listing, per renewal (renews on each sale and every 4 months)
Transaction fee            6.5% of price + shipping + gift wrap (not on US sales tax)
Payment processing (US)    3% + $0.25 on total incl. tax and shipping
Offsite Ads (attributed)   15% (<$10K trailing 365d, optional) / 12% (≥$10K, mandatory); cap $100/order
Etsy Plus (optional)       $10/mo; 15 listing credits + $5 ads credit; unlimited Marketplace Insights
Setup fee                  one-time, shown at onboarding if applicable; reports range $15–29
Regulatory operating fee   country-specific; US rate confirm at onboarding
```
Sources: [Etsy Fees & Payments Policy](https://www.etsy.com/legal/fees/), [Etsy Offsite Ads](https://help.etsy.com/hc/en-us/articles/360000338367-How-Etsy-s-Offsite-Ads-Work), [Wix fee summary](https://www.wix.com/blog/cost-to-sell-on-etsy).

Shorthand for modeling only: **Etsy fee ≈ 9.5% of price + $0.45** when no shipping is charged. Do not use for ledger reconciliation.

### 4.2 Unit economics by layer [M, using V fee stack]

| Product | Price | COGS | Etsy fees | Contribution (organic) | Contribution if Offsite-attributed @15% | Contribution via Share & Save link (+4%) | Contribution on Payhip (5%) |
|---|---:|---:|---:|---:|---:|---:|---:|
| Printable wall art, single | $7.99 | $0 | $1.21 | **$6.78** | $5.58 | $7.10 | $7.59 |
| Printable bundle (8 files) | $19.99 | $0 | $2.35 | **$17.64** | $14.64 | $18.44 | $18.99 |
| Editable template / planner | $12.99 | $0 | $1.68 | **$11.31** | $9.36 | $11.83 | $12.34 |
| POD poster 11×14 (Printify, illustrative) | $24.99 | $12.50 | $2.82 | **$9.67** | $5.92 | $10.67 | n/a (Pop-Up: $12.49) |
| POD 15 oz mug, personalized | $26.99 | $14.00 | $3.01 | **$9.98** | $5.93 | $11.06 | n/a (Pop-Up: $12.99) |
| POD ornament, personalized | $19.99 | $9.50 | $2.35 | **$8.14** | $5.14 | $8.94 | n/a (Pop-Up: $10.49) |
| POD fleece blanket 50×60 | $54.99 | $32.00 | $5.67 | **$17.32** | $9.07 | $19.52 | n/a (Pop-Up: $22.99) |

POD COGS are illustrative placeholders inherited from v2.0's catalog estimates; the engine replaces them with dated Printify catalog quotes before any listing is priced [C]. Share & Save is modeled as 4% of order value refunded against the Etsy bill. Payhip's 5% excludes Stripe/PayPal processing, which Payhip passes through ([Payhip](https://payhip.com/pricing)) [C]. Pop-Up Store contribution assumes Printify charges base cost only ([Printify](https://printify.com/pop-up-store/)); payment processing on Pop-Up is handled by Printify and should be confirmed in the merchant terms [C].

**Reading the table:** a $19.99 digital bundle contributes more than a $55 blanket under Offsite attribution, with zero fulfillment risk. Digital bundles are the engine's default "hero" product type; POD exists to lift AOV on proven designs and to capture gift occasions that digital cannot serve.

### 4.3 Fixed stack: value-engineered tiers

| Tier | Monthly | Contents |
|---|---:|---|
| **Lean (Day 0)** | **≈$51** | Claude Pro $20 (scheduled tasks included on Pro, [Claude Code docs](https://code.claude.com/docs/en/routines)); Etsy Plus $10; eRank Basic $5.99 ([AutoKeyWorder](https://autokeyworder.com/blog/erank-vs-everbee/)); image-generation API ≈$15 at $0.003–0.06/image ([DevelopersDigest](https://www.developersdigest.tech/blog/image-video-generation-api-pricing-2026)); SerpApi free tier 250 searches/mo ([SocialCrawl](https://www.socialcrawl.dev/blog/best-google-trends-apis-2026)); Pinterest API free [C]; Payhip free; Printify free; GitHub free. |
| **Growth (after first 30 paid orders)** | **≈$195** | Claude Max 5x $100 (if Pro usage limits are hit); EverBee Growth $39 monthly or $24.99 annual for Research API access ([AutoKeyWorder](https://autokeyworder.com/blog/everbee-pricing/)) [C]; SerpApi Starter $25; remainder as Lean. |
| **Scale (after $3K/mo contribution)** | **≈$250–300** | Growth + Printify Premium $39 (only if `eligible POD spend × realized discount > $39`); Tailwind if Pinterest API limits bind. |

### 4.4 Day 0–Day 1 deployment of the $1,500

| Item | Amount | Purpose |
|---|---:|---|
| Etsy shop setup fee (as quoted at onboarding) | $15–29 | Required |
| Etsy Plus, month 1 | $10 | Unlimited Marketplace Insights, credits |
| Claude Pro, month 1 | $20 | Engine runtime |
| eRank Basic, month 1 | $6 | Keyword baseline |
| Image generation credits | $30 | ~500–2,000 generations depending on model |
| Listing fees, launch batch (60 digital + 10 POD) | $14 | At $0.20 each |
| Physical samples (2–3 SKUs incl. shipping) | $90 | Required before any POD listing goes live |
| Etsy Ads test budget (weeks 2–6, $3/day) | $105 | Conversion and keyword signal, not scale |
| SerpApi Starter, 1 month (optional) | $25 | Trend momentum data beyond free tier |
| Font / asset licenses (commercial) | $60 | Provenance records |
| **Committed Day 0–1 spend** | **≈$375–390** | |
| Held in reserve: supplier float for POD orders + month 2–3 stack | ≈$650 | Printify charges at order time; Etsy pays 14–20 days later for new sellers |
| Unallocated (ROI-gated expansion: EverBee API, Claude Max, more ads) | ≈$460 | Released only when §10 gates are met |

### 4.5 Payback and owner-yield sensitivity [M]

Assumptions: organic conversion 1.5–3% on qualified visits ([EtsyFlow](https://etsyflow.com/blog/etsy-conversion-rate-2026/)); blended contribution per order from §4.2; Lean fixed stack $51 (Growth $195 from Month 6); owner time 6.5 h/month after build; 25 h build. Visits per listing are assumptions, not observations.

| State | Active listings | Visits/listing/mo | Conv. | Orders/mo | Blended contrib./order | Contribution/mo | Fixed | Operating result | Owner yield $/hr | Cumulative operating result |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Month 1 (launch) | 70 | 8 | 1.5% | 8 | $9 | $76 | $51 | **$25** | $4 | $25 |
| Month 2 | 110 | 15 | 2.0% | 33 | $10 | $330 | $51 | **$279** | $43 | $304 |
| Month 3 | 150 | 22 | 2.0% | 66 | $11 | $726 | $51 | **$675** | $104 | $979 |
| Month 6 | 250 | 30 | 2.5% | 188 | $12 | $2,250 | $195 | **$2,055** | $316 | ≈$5,300 |
| Month 12 | 400 | 35 | 2.5% | 350 | $13 | $4,550 | $250 | **$4,300** | $662 | ≈$27,000 |

Payback reading: the Day 0–1 committed spend (≈$390, §4.4) is recovered during Month 2 in this scenario; the full $1,500 is recovered only if the ROI-gated reserve is actually deployed, and then by roughly Month 4. Payback inside 90 days is plausible only if the first two weekly cycles find at least one niche with real pull; the engine's job in weeks 1–6 is discovery, not revenue. The owner-yield column, not revenue, decides whether to increase spend. The 90-day gate (§10) is set at **positive operating result for two consecutive weeks and owner time ≤ 2 h/week**, which the Month 2–3 rows represent.

### 4.6 Break-even arithmetic

Lean stack break-even: $51 ÷ $10 ≈ **5 orders/month**. Growth stack: $195 ÷ $11 ≈ **18 orders/month**. At 2% conversion that is 250 and 900 qualified visits/month respectively. These are falsifiable traffic requirements the weekly brief reports against.

---

## 5. Architecture

### 5.1 Components

```
┌──────────────────────────── GitHub repo: trend-engine ─────────────────────────────┐
│ main (protected; owner merge required)   ←  weekly PR from engine branch            │
│ data/ (signals, scores, cohorts)  assets/ (masters, previews)  releases/ (manifests)│
│ .github/workflows/executor.yml  → runs ONLY on merge to main                        │
└──────────────┬────────────────────────────────────────────────┬─────────────────────┘
               │ reads/writes via GitHub proxy                  │ secrets (GitHub Actions)
┌──────────────▼─────────────────────────┐        ┌─────────────▼──────────────────────┐
│ Claude Code cloud scheduled tasks       │        │ Executor (GitHub Action, Python)    │
│ Custom network allowlist:               │        │ Allowlisted operations only:        │
│  openapi.etsy.com (read scopes)         │        │  Etsy: create/activate DIGITAL       │
│  api.printify.com (catalog read)        │        │        listings, upload files/images│
│  research-open-api.everbee.com          │        │  Printify: create product, publish  │
│  serpapi.com, image-gen API host        │        │  Pinterest: create pins             │
│ Tasks: sense, define, make, measure,    │        │  Payhip: upload product [C]         │
│        order-guardian, weekly-close     │        │ Idempotent; hashes manifest; logs   │
└─────────────────────────────────────────┘        └─────────────────────────────────────┘
```

- **Cloud scheduled tasks** run on Anthropic-managed infrastructure, can use connected MCP connectors, support schedule/GitHub/API triggers, and have a one-hour minimum interval ([Claude Code docs](https://code.claude.com/docs/en/routines)). Cloud environments support network levels None/Trusted/Custom/Full; Custom takes your own domain allowlist ([Cloud environments](https://code.claude.com/docs/en/cloud-environments)). The engine uses **Custom** with exactly the hosts above.
- **The engine never holds write credentials.** Its Etsy token has read scopes only (`shops_r`, `listings_r`, `transactions_r`, `feedback_r`) [C]. Its Printify token is used for catalog reads only. Write tokens exist only as GitHub Actions secrets consumed by the executor.
- **Approval = PR merge.** Branch protection requires the owner's review. The merge commit SHA, the manifest hash and the approver identity form the immutable approval record v2.0 asked for.
- **Executor** is a small Python package with one function per allowlisted operation. It refuses any manifest whose hash does not match the merged file, enforces ceilings (max listings/run, max ad budget change, max price change %), and writes a result ledger back to the repo.

### 5.2 Single writer per SKU

| SKU type | Catalog owner | Publisher | Etsy writer |
|---|---|---|---|
| Digital download | Repo (`assets/digital/`) | Executor via Etsy API `createDraftListing` (type `download`) + `uploadListingFile` + image upload + state `active` [C] | Executor |
| POD, non-personalized | Printify product | Executor via Printify API create + publish ([Printify API](https://printify.com/blog/powerful-custom-solutions-with-printify-api/)) | Printify |
| POD, personalized (Live Preview) | Printify product, created in Printify Product Creator UI during the weekly session (API support for personalization layers is unconfirmed [C]) | Printify publish | Printify |
| Payhip / Pop-Up mirrors | Same source files | Executor (Payhip) [C]; Printify Pop-Up publish | n/a |

Etsy app registration: eligible sellers' apps are approved within minutes with no manual review queue; commercial access is manual ([Etsy Open API v3](https://developer.etsy.com/documentation/)). Rate limits are discovered from response headers, never assumed.

### 5.3 Data model (minimum)

- `signal`: source, keyword, metric, value, window, retrieved_at, license.
- `concept`: niche, buyer, occasion, visual idea, keywords[], score components, veto flags, status.
- `asset`: concept_id, type (digital|pod), files[], pixel dims, QA results, prompt provenance, font/asset licenses, ai_disclosure=true, checksum.
- `listing`: channel, external_id, sku, type, price, cost_snapshot_id, disclosure_checked, partner_checked (POD), state, version, published_at.
- `cohort`: listing_id, week_launched, visits, orders, contribution, ad_spend, decision.
- `order`: receipt_id, line items, personalization text, flags[], hold_state, supplier_order_id, cost, refund.
- `release_manifest` (YAML): week, actions[] {op, payload, payload_sha256, ceilings}, approver, merge_sha.

### 5.4 Trust tiers

1. First-party APIs and docs (Etsy, Printify, Pinterest, EverBee, SerpApi): preferred.
2. Pinned internal clients with tests: allowed.
3. Third-party MCP servers with write scopes: disabled.
4. GitHub repos (presswork, printify-mcp, etsyv3): read for reference only; licenses checked before copying.

---

## 6. Compliance rails (encoded in the executor, not in prompts)

| Rail | Rule | Source |
|---|---|---|
| AI disclosure | Every listing whose design, mockup or description was AI-assisted must have the AI disclosure set in the listing and a plain disclosure sentence in the description. Executor refuses otherwise. | [Etsy Creativity Standards](https://www.etsy.com/legal/creativity/), [Etsy Seller Policy](https://www.etsy.com/legal/sellers/), [SellersNest enforcement summary](https://sellersnest.com/blog/etsy-ai-disclosure-rules/) |
| Creative role | Prompts, edits and composition decisions are logged per asset so "seller-prompted AI creation" is demonstrable. Running others' prompts does not qualify. | [Etsy Creativity Standards](https://www.etsy.com/legal/creativity/) |
| Production partner | Every POD listing has the Printify partner attached in Etsy before activation; Printify cannot auto-populate this. Weekly session includes a 5-minute partner audit on new POD listings. | [Printify](https://help.printify.com/hc/en-us/articles/4578966175505) |
| Images | First image of a personalized item shows a finished, realistic example; no "Your text here". Mockups must come from the actual provider product. | [Printify](https://help.printify.com/hc/en-us/articles/40720228428433), [Etsy Seller Policy](https://www.etsy.com/legal/sellers/) |
| IP | Automated blocklist (brands, teams, characters, celebrities, lyrics, quotes with known authors) + USPTO lookup + similarity check; any hit = hard veto, no human override in the weekly PR without a written note. | v2.0 §3 |
| Titles/tags | Concise titles (Etsy guidance favors under ~15 words), 13 relevant tags, accurate attributes. | [Etsy listing guidance](https://help.etsy.com/hc/en-us/articles/115015628707) |
| Personalization | Printify personalization schema edited only in Printify; Live Preview never edited on Etsy. | [Printify Live Preview](https://help.printify.com/hc/en-us/articles/48538801703057) |
| Offsite Ads | Opt out while under $10K trailing sales unless the weekly brief shows attributed-order contribution is positive; model 12% lock-in when approaching $10K. | [Etsy Help](https://help.etsy.com/hc/en-us/articles/360000338367-How-Etsy-s-Offsite-Ads-Work) |
| No browser automation of Etsy | Only APIs, native integrations and permitted exports. | [Etsy API Terms](https://www.etsy.com/legal/api/) |
| Buyer data | Personalization text is the only buyer data the engine reads; names/addresses never enter prompts or logs. | v2.0 §8 |
| Star Seller hygiene | Message response within 24 h is automated by a templated auto-reply plus escalation; on-time shipping relies on Printify SLAs; 4.8 rating average is a KPI. | [Etsy Star Seller](https://www.etsy.com/in-en/starseller) |

---

## 7. Build: Day 0 to Day 21

Owner time is given per step. Super prompts (SP) are in §8.

### Day 0 (≈3 h)

1. **Accounts.** Open: Etsy shop (pay the quoted setup fee; enroll Etsy Plus; enroll Share & Save; opt out of Offsite Ads for now); Printify (connect to Etsy; set order approval to manual with 24-hour auto-approve for later); Payhip free; Pinterest Business account; GitHub; Claude Pro; eRank Basic; SerpApi free; one image-generation API account (pick a model with strong text rendering for typographic designs).
2. **Etsy developer app.** Register a Seller App at the Etsy Developer Portal; request read scopes for the engine token and read+write scopes for the executor token; store the keystring and tokens in GitHub Actions secrets ([Etsy Open API v3](https://developer.etsy.com/documentation/)).
3. **Repo.** Create `trend-engine` from SP-01. Enable branch protection on `main` requiring one review.
4. **Cloud environment.** In Claude Code, create a cloud environment with Custom network access listing exactly the API hosts in §5.1; connect the GitHub repo ([Cloud environments](https://code.claude.com/docs/en/cloud-environments)).

### Day 1 (≈2 h)

5. Run SP-01 (scaffold) as a one-off cloud task; review the generated repo PR; merge.
6. Create scheduled tasks from §8.0 table: `sense` daily 06:07, `measure` daily 07:07, `order-guardian` every 6 h, `define+make` weekly Thursday 03:07, `weekly-close` weekly Friday 05:07. Pick a few minutes past the hour as the docs advise ([Claude Code docs](https://code.claude.com/docs/en/routines)).
7. Run SP-02 manually once to confirm signals land in `data/signals/`.

### Days 2–7 (≈6 h total)

8. First `define+make` run produces the Week-1 PR: 3 niches, ~12 concepts, ~60 digital listings drafted, 10 POD candidates flagged "awaiting sample".
9. Weekly session #1 (90 min): follow §9.1 runbook. Order 2–3 physical samples from the POD candidates. Merge the PR for digital listings only.
10. Executor publishes digital listings. Verify three listings in a signed-out browser: AI disclosure present, files download correctly, images correct.
11. Create the Pinterest boards the engine proposed; confirm the first pins post with Share & Save links.

### Days 8–14 (≈3 h)

12. Weekly session #2: review cohort data (expect mostly noise); approve Week-2 concepts; approve Etsy Ads at $3/day on the 10 highest-signal listings.
13. When samples arrive, photograph them (phone is fine; these become the real-photo first images), score print quality, and record in `data/samples/`.

### Days 15–21 (≈3 h)

14. Weekly session #3: approve POD listings for sample-passed designs that already have digital sales or top-quartile visits. Attach production partner in Etsy for each; the PR template includes the checklist.
15. Create the first personalized POD product in Printify's Product Creator with Live Preview; place one test order; approve only after the preview renders correctly ([Printify](https://help.printify.com/hc/en-us/articles/40720228428433)).
16. Confirm `order-guardian` is holding only flagged orders and auto-releasing the rest after 24 h.

From Day 22 the only recurring owner task is the weekly session.

---

## 8. Super prompts and operating instructions

### 8.0 Task schedule

| Task | Trigger | Prompt | Writes | Owner |
|---|---|---|---|---|
| `sense` | daily 06:07 | SP-02 | `data/signals/YYYY-MM-DD/` | none |
| `measure` | daily 07:07 | SP-08 | `data/cohorts/`, `data/orders/` | none |
| `order-guardian` | every 6 h | SP-09 | `data/orders/holds.json`, alert | releases holds weekly or on alert |
| `define-make` | weekly Thu 03:07 | SP-03 then SP-04, SP-05, SP-06 | PR `release/week-NN` | reviews |
| `weekly-close` | weekly Fri 05:07 | SP-10 | `reports/weekly/`, appended to PR | reads |
| `monthly-gate` | monthly 1st 04:07 | SP-11 | `reports/monthly/` | decides |
| `compliance-watch` | daily 08:07 | SP-12 | `reports/incidents/` | acts on red alerts |
| executor | on merge to `main` | SP-07 (code) | external writes, `data/ledger/` | none |

All prompts assume the `CLAUDE.md` charter (SP-00) is in the repo root.

---

### SP-00: Operating charter (`CLAUDE.md`)

```markdown
# Trend-to-Revenue Engine — Operating Charter v3.0

## Mission
Maximize owner yield ($/owner-hour) by sensing marketplace trends, defining original digital and
print-on-demand offers, producing compliant assets and listings, distributing them, measuring
cohorts, and proposing redefinitions every week. You PROPOSE; the owner APPROVES by merging a PR;
the executor PUBLISHES. You never publish, spend, or message buyers directly.

## Hard rules (also enforced in code)
1. No external writes from any scheduled task. All writes go through releases/*.yaml → PR → executor.
2. Every AI-assisted asset or text is flagged ai_assisted=true and every listing draft includes the
   AI disclosure attribute and a plain-language disclosure sentence.
3. No brands, teams, characters, celebrities, lyrics, attributed quotes, logos, or lookalikes.
   Any IP uncertainty = veto. Record the reason.
4. Never read or store buyer names, addresses, emails, or uploaded photos. Personalization TEXT only.
5. Never claim a demand figure is "Etsy data" unless it came from Etsy Marketplace Insights or the
   Etsy Open API. Label EverBee/eRank/SerpApi numbers as estimates with source and date.
6. Costs come only from dated snapshots in data/costs/. Expired (>14 days) = re-fetch before pricing.
7. A listing is never "killed" on views alone; use the cohort decision rules in docs/redefine.md.
8. Fail closed: missing evidence, insufficient pixels, 401/403/429, or unknown state → stop and report.
9. Respect rate limits from response headers; exponential backoff with jitter; honor Retry-After.
10. Write everything as files in the repo with a dated path. The PR description is the owner's brief.

## Style
Original, differentiated, gift-worthy. Favor textured, painterly, typographic-craft aesthetics over
glossy renders. Concise listing titles (≤15 words), 13 specific tags, accurate attributes.

## Repo map
data/signals, data/scores, data/costs, data/cohorts, data/orders, assets/digital, assets/pod,
assets/pins, releases/, reports/weekly, reports/monthly, reports/incidents, docs/, src/, tests/
```

**Instructions.** Save as `CLAUDE.md`. Adjust the style line when the engine's niche weights shift (it will propose edits in the weekly PR).

---

### SP-01: Day-0 scaffold

```text
You are bootstrapping the trend-engine repository described in CLAUDE.md. Create:
1. The directory map, .gitignore (ignore data/orders/raw, assets/**/masters/*.psd, .env), and
   .env.example listing variable NAMES only: ETSY_KEYSTRING, ETSY_READ_TOKEN, PRINTIFY_READ_TOKEN,
   EVERBEE_CLIENT_ID, EVERBEE_CLIENT_SECRET, SERPAPI_KEY, IMAGE_API_KEY, PINTEREST_TOKEN.
2. config/engine.yaml with: owner_hours_cap_per_week: 1.5; max_new_listings_per_week: 60;
   max_pod_candidates_per_week: 10; etsy_ads_daily_cap_usd: 3; price_floor_margin: 0.60 (digital),
   0.30 (pod, before ads); offsite_ads_opted_in: false; niches_active_max: 3.
3. config/blocklist.yaml seeded with categories (brands, sports leagues, entertainment franchises,
   celebrities, song lyrics, attributed quotes, universities, military insignia, national park
   logos) and a regex set. Include a README on how to extend it.
4. schemas/*.json for signal, concept, asset, listing, cohort, order, release_manifest (fields in
   docs/data-model.md; mirror them).
5. src/clients/ with thin, tested, read-only clients: etsy_read.py (findAllListingsActive by
   keyword with price and favorites; getShopReceipts; getListing stats where available),
   printify_catalog.py (blueprints, print providers, variants, shipping costs),
   everbee.py (headers client_id/client_secret; respect x-remaining-* headers; backoff on 429),
   serpapi_trends.py (google_trends interest_over_time and related_queries),
   image_gen.py (generate with seed, size, prompt; store prompt provenance JSON next to output).
6. src/qa/print_qa.py: check pixel dimensions vs required print size at 300 ppi, bleed, safe zone,
   contrast ratio for text layers, sRGB profile, transparency where required, file size.
7. src/scoring/score.py implementing the niche/offer score in docs/scoring.md.
8. .github/workflows/executor.yml that runs ONLY on push to main when releases/*.yaml changed,
   and src/executor/ with allowlisted operations: etsy_create_digital_listing, etsy_upload_file,
   etsy_upload_image, etsy_activate_listing, etsy_update_price, etsy_deactivate_listing,
   printify_create_product, printify_publish, pinterest_create_pin, payhip_create_product.
   Each op: validate payload against schema, verify payload_sha256, enforce ceilings in
   config/engine.yaml, idempotency key = manifest_id+op_index, read back after write, append
   result to data/ledger/YYYY-MM-DD.jsonl. Secrets only from GitHub Actions secrets.
9. tests/ with fixtures for every client and executor op, including a 429 replay and a duplicate
   manifest replay test that must NOT produce a second write.
10. docs/: data-model.md, scoring.md, redefine.md (cohort decision rules from the playbook §9.3),
    weekly-session.md (runbook from §9.1), PR template with the compliance checklist.
Open a PR titled "Day-0 scaffold". Do not call any external API except to run read-only smoke
tests if credentials are present in the cloud environment secrets.
```

**Instructions.** Run once as a one-off cloud task. Review the PR for secrets leakage (none allowed), run tests, merge. Then add real tokens as GitHub Actions secrets (write tokens) and cloud-environment secrets (read tokens).

---

### SP-02: Sense (daily)

```text
Run the daily SENSE cycle. Date: {{today}}. Output folder: data/signals/{{today}}/.
Sources, in priority order, each saved as its own JSON with source, retrieved_at, license note:
A. Etsy Open API (official): for every keyword in data/keywords/active.yaml and
   data/keywords/candidates.yaml, call findAllListingsActive (limit 100, sort by score) and record:
   result count, price quartiles, share of listings with 'digital download' type, share mentioning
   'personalized', median favorites of top 25, and the top 25 titles' n-gram frequencies.
   This is COMPETITION data, not demand data. Label it so.
B. EverBee Research API (estimate): keyword volume/competition estimates and top-listing monthly
   sales estimates for the same keywords. Label 'estimate'. Skip gracefully if credentials absent.
C. SerpApi Google Trends (estimate): interest_over_time (90d and 5y) and rising related_queries
   for each active niche head term. Compute 4-week slope and year-over-year seasonality index.
   Stay within 8 queries/day on the free tier unless config says otherwise.
D. Etsy Seller Handbook trend reports: if a new report exists in data/trend_reports/ (owner pastes
   the URL into data/trend_reports/queue.txt), extract trend names, growth %, categories, dates.
E. Candidate discovery: from rising related_queries and Etsy title n-grams, propose up to 20 NEW
   keywords for data/keywords/candidates.yaml with a one-line rationale each.
Write data/signals/{{today}}/summary.md: top 10 movers (up/down), new candidates, any API errors,
remaining rate-limit headroom. No external writes. Commit to branch signals/{{today}} and open or
update the rolling PR 'signals: week {{iso_week}}' (auto-merge allowed; it touches only data/).
```

**Instructions.** The signals PR is the one PR that may auto-merge (data only). Everything else waits for the weekly PR. Owner adds Etsy trend-report URLs to `data/trend_reports/queue.txt` when Etsy publishes them (roughly twice a year plus holiday updates).

---

### SP-03: Define (weekly)

```text
Run DEFINE for ISO week {{iso_week}}. Inputs: data/signals/ (last 14 days), data/cohorts/
(all), data/costs/ (<14 days old), config/engine.yaml, docs/scoring.md.
1. Build a niche table (max 25 candidates): for each niche compute
   demand_momentum (Trends slope + EverBee delta, estimates), competition_gap (Etsy result count
   vs top-25 median favorites; low count + high favorites = gap), gift_intent (occasion words,
   'personalized' share), digital_fit (can a printable/template/SVG serve it well?),
   pod_fit (which blueprints; landed cost; margin at floor), seasonality (weeks to next peak),
   ip_risk (blocklist hits; veto if any), our_evidence (orders/visits from cohorts).
   Score 0–100 with weights in docs/scoring.md. Veto before scoring.
2. Select up to niches_active_max niches. Explain each in ≤5 lines with the specific signals.
   If an existing active niche loses its slot, say why and what happens to its listings
   (retire at renewal, never delist selling items).
3. For each selected niche, propose up to 4 concepts (≤12 total): buyer, occasion, original visual
   idea, primary keyword, 12 secondary keywords, product forms (digital single, digital bundle,
   editable template, POD poster/mug/ornament/blanket), suggested prices with margin at floor,
   nearest substitutes (titles only), and a 'why this is not generic' sentence.
4. Mark each concept DIGITAL_FIRST (default) or POD_ELIGIBLE (only if it has a cohort with ≥3
   digital sales or top-quartile visits and a passed sample, or is a personalized gift form with
   strong gift_intent).
5. Write data/scores/{{iso_week}}/niches.json, concepts.json, and define.md (the owner brief).
Stop here; MAKE runs next in the same session only if concepts.json validates against schema.
```

**Instructions.** Review `define.md` in the weekly PR. Edit scores or weights by committing to `docs/scoring.md`; the next run uses them. Hard vetoes cannot be overridden in the PR without a written `OVERRIDE:` note, which is logged.

---

### SP-04: Make (weekly, runs after SP-03)

```text
Run MAKE for the approved-for-drafting concepts in data/scores/{{iso_week}}/concepts.json.
For each concept:
1. Generate 3 visual directions with the image API; choose 1 by a rubric (originality, print
   legibility, fit to Etsy 'Mark of the Maker' aesthetic, no text artifacts). Save prompts, seeds,
   model, and your composition edits to assets/**/provenance.json. ai_assisted=true.
2. Produce masters at exact print pixel sizes: digital prints at 2:3, 3:4, 4:5, A-series and
   11x14 ratios (300 ppi equivalents); POD masters at the Printify blueprint's print-area pixels
   from data/costs/. Run src/qa/print_qa.py; fail the asset if any check fails and note why.
3. Build digital deliverables: ZIP of PDFs/JPGs per ratio + a README-for-buyer PDF (how to print,
   license: personal use only). For bundles, 6–12 coordinating files.
4. Build mockups: digital = tasteful room/frame mockups from licensed templates in assets/mockups
   (keep license record); POD = Printify-generated mockups from the actual blueprint. For
   personalized items, use a realistic example name, never 'Your Name Here'.
5. Build pin images: 2 vertical 1000x1500 variants per listing with a short text overlay.
6. Write a contact sheet reports/weekly/{{iso_week}}/contact_sheet.md with thumbnails, QA status,
   and provenance links.
Do not create or publish anything externally. Stop and report if the image API budget in
config/engine.yaml would be exceeded.
```

**Instructions.** The owner looks at the contact sheet during the weekly session. Anything that looks derivative or low quality is removed by deleting its line from the manifest before merge.

---

### SP-05: Listing composer (weekly, after SP-04)

```text
For each QA-passed asset, draft the listing in data/listings/{{iso_week}}/{{sku}}.json:
- title ≤ 140 chars and ≤ 15 words, specific, no keyword stuffing;
- 13 tags from the concept's keyword set (no duplicates of title words where avoidable);
- category, attributes, occasion, recipient, style;
- description: what it is, exact deliverables or product specs, how to print/care, personalization
  instructions if any, the AI disclosure sentence ('This design was created by the seller using
  AI image tools from the seller's original prompts and then edited; see shop policies.'),
  and for POD 'Produced by a production partner; see partner disclosure';
- price per docs/pricing.md: digital singles $6.99–9.99, bundles $14.99–24.99, templates
  $9.99–16.99; POD = landed cost ÷ (1 − 0.095) + $0.45 + target contribution, rounded to .99,
  and must clear price_floor_margin at the worst variant;
- shipping profile (POD only), processing time from the provider snapshot;
- cross-links: digital ↔ POD sibling SKUs;
- a margin table per variant using the dated cost snapshot.
Then write releases/week-{{iso_week}}.yaml with one action per publish, each including
payload_sha256, and the ceilings from config/engine.yaml. Include pins (SP-06 output) and any
price/retire actions from the previous weekly-close decisions.
Open PR 'release/week-{{iso_week}}' using the PR template; attach define.md, contact_sheet.md,
and last weekly brief. No external writes.
```

**Instructions.** This PR is the weekly approval object. Merging it triggers the executor.

---

### SP-06: Marketing distribution (weekly, after SP-05; daily pin cadence by executor)

```text
Build the distribution plan for week {{iso_week}} in data/marketing/{{iso_week}}/:
1. Pinterest: for each new listing, 2 pins (from assets/pins) with title ≤100 chars, description
   ≤500 chars with 3–5 natural keywords, destination = Etsy listing URL wrapped in the shop's
   Share & Save link; for digital SKUs also 1 pin pointing to the Payhip mirror. Assign boards by
   niche; propose new boards if none fit. Spread publish timestamps across the next 7 days at
   ≤ 8 pins/day. Output pins.yaml for the executor.
2. Etsy Ads: given cohort data, propose which listings get the $3/day budget (max 10 listings);
   never raise the daily cap without an owner note in the PR. Output ads.yaml (owner applies
   manually in Shop Manager during the weekly session; Etsy Ads has no write API).
3. Share & Save: ensure every outbound link in pins and the Payhip store uses the tracking link.
4. Seasonal: compare the calendar in data/calendar.yaml to today; if a peak is 8–10 weeks out,
   add a 'seasonal collection' concept request to next week's DEFINE queue.
Append the plan summary to the release PR. No external writes.
```

**Instructions.** Pinterest API access begins with a trial tier and requires app review for higher limits [C]; if posting fails on limits, switch the executor's pin op to Tailwind's API or scheduler. Etsy Ads changes are the one marketing action the owner clicks manually (≈3 minutes/week).

---

### SP-07: Executor (code, not a prompt)

Behavior specification for `src/executor/` (generated by SP-01, maintained by the engine via PRs):

```text
on push to main where releases/*.yaml changed:
  load manifest; verify git merge commit is on main and has ≥1 approving review (GitHub API)
  for each action in order:
    verify payload_sha256 == sha256(canonical_json(payload))
    verify op in ALLOWLIST and ceilings not exceeded (count, price delta %, ad budget)
    verify compliance preconditions: ai_disclosure==true for ai_assisted; description contains
      disclosure sentence; POD actions include partner_checked==true (owner ticks in PR template)
    if idempotency key exists in ledger: skip, log 'duplicate'
    execute with retries honoring Retry-After; on 401/403: stop entire run, alert
    read back the created object; store external id, state, timestamp in ledger
  write data/ledger/{{date}}.jsonl; open PR 'ledger: week NN' (auto-merge, data only)
  post summary to the release PR as a comment
```

**Instructions.** Keep the allowlist short. Any new op requires a code PR reviewed by the owner.

---

### SP-08: Measure (daily)

```text
Run MEASURE for {{today}}. Read-only.
1. Etsy: getShopReceipts since last run; for each receipt record listing ids, quantities, price,
   shipping, personalization TEXT only (no buyer identity), is_digital, Offsite-attributed flag if
   exposed, and fees where the API provides them. Store in data/orders/{{today}}.json.
2. Pull listing-level stats available via API; for metrics the API does not expose (views, visits
   by source), read the latest owner-uploaded Shop Stats CSV in data/stats_exports/ and note its
   date. If older than 8 days, add 'upload stats CSV' to the weekly session checklist.
3. Printify: list orders and costs for the period; join to Etsy receipts by external id.
4. Update data/cohorts/cohorts.json: per listing, cumulative visits, orders, revenue, fees,
   POD cost, ad spend (from ads.yaml), contribution, days live, renewal date.
5. Compute: contribution per 100 visits per listing; shop conversion; owner-time log (from
   data/time_log.csv the owner appends during sessions); owner yield MTD.
Write reports/daily/{{today}}.md (≤ 20 lines). No external writes.
```

**Instructions.** Once a week during the session, export Shop Stats (visits by listing and by source) from Shop Manager and drop the CSV in `data/stats_exports/` (2 minutes). Log session minutes in `data/time_log.csv`.

---

### SP-09: Order guardian (every 6 hours)

```text
Check new receipts in data/orders/ not yet triaged.
Flag an order for HOLD if any of: personalization text contains blocklist terms, profanity, a
brand/team/character, > 2 lines where 1 is expected, > the layer's character capacity, emoji or
unsupported glyphs, obvious typos of common names (suggest correction), or a mismatch between
the chosen variant and the personalization field count. Also flag: duplicate receipt ids, a
Printify order with no matching Etsy receipt, a receipt with no Printify order after 6 hours
(POD only), or a digital order where the file download failed.
For flagged POD orders: write data/orders/holds.json with reason and suggested action
(release / message buyer with a drafted question / cancel-refund). The executor's Printify
'hold' op will be invoked only via the weekly PR unless a red alert is raised.
Red alert (open a GitHub issue labeled 'red' and summarize in the next daily report) if: any
hold older than 20 hours (Printify auto-approval is set to 24 h), any policy notification
pattern appears in shop data, or more than 3 holds in a day.
Unflagged orders need no action; Printify auto-approves at 24 h.
```

**Instructions.** Set Printify to manual approval with a 24-hour auto-approve window ([Printify](https://help.printify.com/hc/en-us/articles/4483625253265)). Enable GitHub issue notifications to your phone for the `red` label only. This is the one way the engine can interrupt the owner between sessions.

---

### SP-10: Weekly close and redefine (weekly)

```text
Produce reports/weekly/{{iso_week}}/brief.md (one page) and decisions.yaml.
Brief: orders, revenue, fees (itemized incl. Offsite-attributed orders at their actual rate),
POD cost, ad spend, contribution, fixed stack, operating result, owner minutes, owner yield $/hr,
conversion by traffic source, Pinterest clicks → Etsy visits, Share & Save credits, holds and
incidents, API quota headroom, cash position (Etsy available vs reserved vs pending; Printify
charges due).
Cohort decisions per docs/redefine.md:
 - PROMOTE to POD: digital SKU with ≥3 sales or top-quartile contribution/100 visits and a
   passed sample for the proposed blueprint.
 - BUNDLE: ≥2 selling singles in the same concept → propose bundle SKU.
 - REPRICE: test +10% on SKUs with conversion > 2× shop median; −10% on SKUs with high visits
   and conversion < 0.5× median (max one change per SKU per 4 weeks).
 - RETIRE AT RENEWAL: no sales, visits below shop median, and age ≥ 8 weeks; never auto-renew.
   Do NOT retire on '100 views no sale' alone; show the zero-sale probability at the shop
   conversion rate.
 - NICHE WEIGHT: shift next week's concept allocation toward niches with the best contribution
   per listing; drop a niche only after 6 weeks of bottom-quartile results.
 - ADS: keep budget only on listings with ROAS ≥ 3 over the last 14 days.
Compare actuals to the §4.5 sensitivity row for this month; state which assumption is off.
Append brief.md to the open release PR and add decisions to next week's manifest queue.
```

**Instructions.** The brief is the first thing the owner reads in the session. Decisions take effect only when the next release PR is merged.

---

### SP-11: Monthly gate (1st of month)

```text
Evaluate the gates in docs/gates.md (playbook §10) against the last 4 weekly briefs.
Recommend exactly one of: HOLD (no stack changes), EXPAND (name the specific spend, its expected
payback in days with arithmetic, and the kill condition), or CONTRACT (what to pause).
Specifically evaluate: Claude Pro → Max (are scheduled tasks hitting usage limits?), EverBee
Research API (did signal quality limit DEFINE?), SerpApi Starter, Printify Premium (eligible
spend × realized discount vs $39), Offsite Ads opt-in (attributed-order contribution positive?),
Etsy Ads cap change, a second Etsy shop (no, unless two niches are fully independent brands),
TikTok Shop readiness (only if a video pipeline costs < 30 owner-minutes/week), Shopify (only if
owned-store revenue > 10× its fee). Write reports/monthly/{{month}}.md.
```

---

### SP-12: Compliance watch (daily)

```text
Scan: data/orders for buyer messages flagged by the owner (the owner forwards policy emails into
data/inbox/ as text), the ledger for listings missing disclosure or partner flags, Printify for
blueprint discontinuations or cost changes > 5% vs snapshot, Etsy API responses for new deprecation
headers, and config/blocklist.yaml for required updates from new signals (new brand/franchise
terms appearing in rising queries). Produce reports/incidents/{{today}}.md only if something is
found; otherwise write 'clean'. Red-label a GitHub issue for: policy notice, IP complaint, cost
change > 10%, publish failures > 10% in the last executor run, or Star Seller metric at risk.
```

---

## 9. Operate into perpetuity

### 9.1 Weekly review runbook (target 60–90 minutes)

| Min | Step | Where |
|---|---|---|
| 0–10 | Read `brief.md`; note owner yield and the single most-off assumption | PR |
| 10–20 | Resolve holds in `holds.json`: release, message buyer (paste drafted message in Etsy), or refund | Etsy, Printify |
| 20–35 | Review `define.md`: accept niche set or edit weights in `docs/scoring.md` | PR |
| 35–55 | Skim `contact_sheet.md`; delete weak assets' lines from the manifest | PR |
| 55–65 | Validate the top 5 new keywords in Etsy Marketplace Insights (unlimited with Etsy Plus); paste a screenshot or CSV into `data/insights/` | Shop Manager |
| 65–75 | Tick the PR checklist: partner attached on new POD listings (Shop Manager), disclosure sentence spot-checked on 3 listings, ads changes applied per `ads.yaml` | Shop Manager |
| 75–80 | Export Shop Stats CSV to `data/stats_exports/`; append minutes to `data/time_log.csv` | Shop Manager, repo |
| 80–85 | Merge the release PR | GitHub |
| 85–90 | Watch the executor summary comment; confirm no red issues | GitHub |

If the session exceeds 2 hours for two consecutive weeks, the monthly gate must propose a labor fix (fewer concepts/week, stricter QA thresholds, or more automation) before any revenue expansion.

### 9.2 Monthly and seasonal cadence

- **Monthly:** SP-11 gate; rotate Etsy Ads spend; review Offsite Ads position relative to the $10K threshold.
- **Seasonal (from `data/calendar.yaml`):** Valentine's, Mother's/Father's Day, graduation, wedding season, back-to-school, Halloween, Thanksgiving/Friendsgiving, Christmas/Hanukkah, New Year planners. Launch collections 8–10 weeks ahead; stop new seasonal POD listings when the provider's holiday cutoff is inside the processing window.
- **Twice yearly:** when Etsy publishes a Seller Trend Report, paste the URL into `data/trend_reports/queue.txt`; the engine extracts it the next morning.

### 9.3 Redefine rules (the perpetuity mechanism, summarized)

1. Listing fee budget is the scarce resource: renewals ($0.20) go only to SKUs with positive 8-week contribution or to new tests; losers lapse.
2. Niche allocation follows contribution per listing, with a six-week minimum before a niche is dropped and a two-week fast-track to add one with strong momentum.
3. Promotion ladder: digital single → digital bundle → POD sibling → personalized POD sibling; each step requires evidence from the step before.
4. Pricing moves in ±10% steps with a four-week cool-down per SKU.
5. The style line in `CLAUDE.md` is revised monthly from what sold, not from what was predicted.
6. Any rule change is a PR to `docs/redefine.md`, so the rulebook has a history.

---

## 10. KPIs and gates

### 10.1 KPIs (reported weekly)

Owner yield $/hr; operating result; contribution per 100 visits per SKU; shop conversion by source; orders and AOV; digital vs POD mix; Pinterest click-through to Etsy and Payhip; Share & Save credits; hold rate and resolution time; publish defect rate; API 429 count; cash available vs committed Printify charges; Star Seller metrics (response rate, on-time shipping, rating).

### 10.2 Gates

| Gate | Criteria | Action if met | Action if missed |
|---|---|---|---|
| Day 7 | ≥50 digital listings live with disclosures; executor ledger clean; pins posting | continue | fix pipeline before adding concepts |
| Day 21 | 2+ samples passed; first POD listings live with partner attached; personalized test order rendered correctly | enable personalized POD | keep digital-only |
| Day 45 | Any niche with ≥10 orders or contribution/100 visits above $15 | shift 50% of new concepts to it; start bundle ladder | broaden candidates; do not add spend |
| Day 90 | Operating result positive for 2 consecutive weeks; owner time ≤ 2 h/week; no unresolved policy issues | release ROI-gated budget per SP-11 (EverBee API, Claude Max, ads to $10/day) | HOLD; run 4 more cycles; if still negative, CONTRACT to digital-only lean stack |
| $8K trailing sales | approaching the $10K Offsite Ads lock-in | reprice POD to absorb 12% on attributed orders; decide opt-in deliberately | n/a |
| Month 6 | Owner yield ≥ $150/hr for 8 weeks | consider owned-store ads (Pinterest ads) with a 30-day payback test | keep organic |
| Month 12 | Repeatability across ≥3 niches | evaluate TikTok Shop pipeline and productizing the engine | continue |

### 10.3 Pause triggers (any one)

Negative contribution after variable costs for 3 consecutive weeks; IP complaint or policy notice; inability to fund committed Printify charges; executor publishing without a merged manifest (security breach); hold backlog older than 24 hours.

---

## 11. Risk register

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| AI-disclosure enforcement removes listings | Medium | High | Executor hard-stop; weekly spot-check; attribution set to "Designed by" |
| Digital download saturation lowers conversion | High | Medium | Differentiated aesthetics; bundles; personalized POD ladder; niche rotation |
| Pinterest ramp slower than modeled | High | Medium | It costs nothing but pins; Etsy organic remains primary; Etsy Ads test provides signal |
| Pinterest/Etsy/Printify API quota or access changes | Medium | Medium | Header-driven limits; Tailwind fallback; manual publish fallback via Printify UI |
| Payment reserve starves POD float | Medium | Medium | Digital-first cash; $650 reserve; tracking uploads release reserves |
| Prompt injection via buyer personalization text | Low | High | Personalization text treated as data, never as instructions; blocklist; holds |
| Claude Pro usage limits throttle scheduled tasks | Medium | Low | Monthly gate upgrades to Max when tasks are skipped |
| Owner time creeps above 90 min | Medium | High (defeats objective) | Time log; labor-fix-before-expansion rule |
| Provider cost increases | Medium | Medium | 14-day snapshot expiry; compliance watch flags >5% |
| Offsite Ads lock-in at $10K | Certain at scale | Medium | Pre-emptive pricing; opt-in decision at $8K |

---

## 12. Sources

Primary and dated sources used in this revision:

- Etsy Fees & Payments Policy: https://www.etsy.com/legal/fees/
- Etsy Seller Policy (last updated 5 Oct 2026): https://www.etsy.com/legal/sellers/
- Etsy Creativity Standards: https://www.etsy.com/legal/creativity/
- Etsy Offsite Ads rules: https://help.etsy.com/hc/en-us/articles/360000338367-How-Etsy-s-Offsite-Ads-Work
- Etsy Share & Save and Creator Collective: https://www.etsy.com/seller-handbook/article/1503753198977
- Etsy Marketplace Insights: https://www.etsy.com/seller-handbook/article/1404564905677
- Etsy Seller Trend Report Fall & Winter 2026 (14 Oct 2026): https://www.etsy.com/seller-handbook/article/1521255894814
- Etsy on AI use: https://www.etsy.com/seller-handbook/article/1402347260856
- Etsy Open API v3 and app approval: https://developer.etsy.com/documentation/
- Etsy API Terms: https://www.etsy.com/legal/api/
- Etsy payment account reserve: https://help.etsy.com/hc/en-us/articles/360058722214-What-is-a-Payment-Account-Reserve
- Etsy Star Seller: https://www.etsy.com/in-en/starseller
- Etsy listing guidance: https://help.etsy.com/hc/en-us/articles/115015628707
- Etsy digital download fee table and worked examples: https://www.feeproofed.com/guides/etsy-fees-for-digital-downloads-2026/
- Etsy AI disclosure enforcement summary (Jan 2026, Q1 removals): https://sellersnest.com/blog/etsy-ai-disclosure-rules/
- Etsy sellers and AI saturation (Digital Trends): https://www.digitaltrends.com/computing/etsy-sellers-are-quitting-as-ai-slop-floods-the-handmade-marketplace/
- Etsy conversion benchmarks: https://etsyflow.com/blog/etsy-conversion-rate-2026/
- Etsy setup fee range and fee summary (Wix): https://www.wix.com/blog/cost-to-sell-on-etsy
- Etsy deposit timing for new sellers (Growtsy): https://www.growtsy.com/tools/etsy-deposit-checker
- Printify pricing: https://printify.com/pricing/
- Printify Etsy automated personalization: https://help.printify.com/hc/en-us/articles/40720228428433
- Printify Live Preview constraints: https://help.printify.com/hc/en-us/articles/48538801703057
- Printify production-partner limitation: https://help.printify.com/hc/en-us/articles/4578966175505
- Printify order approval settings: https://help.printify.com/hc/en-us/articles/4483625253265
- Printify API overview: https://printify.com/blog/powerful-custom-solutions-with-printify-api/
- Printify API rate limits: https://developers.printify.com/rate-limits
- Printify Pop-Up Store: https://printify.com/pop-up-store/
- Payhip pricing: https://payhip.com/pricing
- Amazon Merch royalty tiers from 1 June 2026: https://merchtitans.com/blog/amazon-merch-royalty-changes-june-2026
- TikTok Shop US referral fee change 4 Aug 2026: https://www.hubfluence.io/tiktok-shop-seller-fees ; fee history: https://marginory.com/data/tiktok-shop-fee-history
- Shopify pricing: https://www.shopify.com/pricing ; Starter plan closure: https://webmedic.com/shopify-starter-plan-guide
- Redbubble fee caveat: https://websocial.ca/best-print-on-demand-sites-for-artists-2026/
- Claude Code scheduled tasks: https://code.claude.com/docs/en/routines
- Claude Code cloud environments and network access: https://code.claude.com/docs/en/cloud-environments
- Claude Code session-scoped scheduling and /loop: https://code.claude.com/docs/en/scheduled-tasks
- Claude plans: https://claude.com/pricing?mode=code
- EverBee Research API developer guide: https://research-open-api.everbee.com/docs/research-open-api-guide.html
- EverBee pricing: https://autokeyworder.com/blog/everbee-pricing/ ; eRank vs EverBee: https://autokeyworder.com/blog/erank-vs-everbee/
- Google Trends API status and SerpApi pricing: https://www.risingtrends.co/blog/google-trends-api ; https://www.socialcrawl.dev/blog/best-google-trends-apis-2026
- Pinterest Trends has no public API: https://apify.com/data_ops_main/pinterest-trends
- Tailwind pricing: https://support.tailwindapp.com/en/articles/17232111-tailwind-plans-and-pricing
- Image generation API price ranges: https://www.developersdigest.tech/blog/image-video-generation-api-pricing-2026
- Printify's 2026 best-selling Etsy categories (press release, qualitative): https://natlawreview.com/press-releases/printify-reveals-best-selling-items-etsy-2026

**Before spending, verify in live accounts [C]:** Etsy setup fee quote; Etsy Seller App scopes and exact digital-listing endpoints; Printify API support for personalization layers; Pinterest API trial limits; Payhip API availability; EverBee Research API plan requirement; current Printify blueprint costs; Claude Pro scheduled-task usage headroom.
