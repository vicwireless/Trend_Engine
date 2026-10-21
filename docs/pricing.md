# Pricing

Source: playbook v3.0 SP-05 and §4 (`docs/playbook-v3.0.md`). The listing composer prices with
these rules; the executor independently refuses any price below `price_floor_margin` using the
dated snapshots in `data/costs/`.

## Bands (SP-05)

| Product | Price band |
|---|---|
| Digital single | $6.99–9.99 |
| Digital bundle (6–12 files) | $14.99–24.99 |
| Editable template / planner | $9.99–16.99 |

## POD formula (SP-05)

```
price = landed_cost ÷ (1 − 0.095) + $0.45 + target_contribution, rounded up to .99
```

It must clear `price_floor_margin.pod` (0.30, before ads) at the **worst** variant. `landed_cost` is
the Printify base cost plus shipping from a snapshot ≤ 14 days old.

The 9.5% + $0.45 shorthand is for modeling only. Margin checks and the ledger use the full fee
stack in `data/costs/*-channel-fees.json` (playbook §4.1):

| Line | Rate |
|---|---|
| Listing / renewal | $0.20 per listing, per renewal |
| Transaction | 6.5% of price + shipping + gift wrap |
| Payment processing (US) | 3% + $0.25 on the total incl. tax and shipping |
| Offsite Ads (attributed) | 15% under $10K trailing 365-day sales (optional); 12% at or above (mandatory); cap $100/order |
| Share & Save | 4% of order value back on orders from your own links (6.5% for the first two weeks) |
| Payhip (free plan) | 5% + card processing passed through [C] |

## Reprice

±10% steps, one change per SKU per 28 days (`docs/redefine.md` R-REPRICE-*). Enforced by the executor.

## Offsite Ads

Opted out while under $10K trailing sales (`offsite_ads_opted_in: false`). At $8K trailing sales the
monthly gate reprices POD to absorb 12% on attributed orders and the owner decides opt-in
deliberately (§10.2).
