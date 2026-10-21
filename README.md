# Trend_Engine

Trend-to-Revenue Engine for an Etsy shop: sense trends, define original digital and print-on-demand
offers, produce compliant assets and listings, publish through an approval-gated executor, measure
cohorts, and redefine weekly. The operating charter is [CLAUDE.md](CLAUDE.md); the full operating
playbook (v3.0, 21 Oct 2026) is archived at [docs/playbook-v3.0.md](docs/playbook-v3.0.md).

**The model proposes, the owner approves by merging, the executor publishes.**

## Layout

| Path | What |
|---|---|
| `config/` | `engine.yaml` ceilings, `blocklist.yaml` IP veto list ([how to extend](config/README.md)) |
| `schemas/` | JSON Schemas for records (mirror [docs/data-model.md](docs/data-model.md)) and `ops/` payloads |
| `src/clients/` | Read-only clients: Etsy, Printify catalog, EverBee, SerpApi Trends, image generation |
| `src/qa/print_qa.py` | Print-file QA |
| `src/scoring/score.py` | Niche/offer score ([docs/scoring.md](docs/scoring.md)) |
| `src/executor/` | Allowlisted write ops, run only by `.github/workflows/executor.yml` |
| `data/` | signals, scores, costs, cohorts, orders (raw is gitignored), ledger |
| `assets/` | digital, pod, pins (`masters/*.psd` gitignored) |
| `releases/` | Release manifests. Merging one to `main` triggers the executor |
| `reports/` | weekly, monthly, incidents |
| `docs/` | [playbook](docs/playbook-v3.0.md), data model, scoring, [redefine](docs/redefine.md), [weekly session](docs/weekly-session.md), [pricing](docs/pricing.md), [gates](docs/gates.md) |

## Develop

```bash
pip install -r requirements-dev.txt
pytest -q
python -m src.executor.run --dry-run releases/<file>.yaml   # preflight a manifest, no writes
python -m src.executor.hashing releases/<file>.yaml         # print payload hashes
python -m src.qa.print_qa assets/pod/x.png spec.json        # QA a print file
```

## Secrets

Never commit secrets. `.env.example` lists the read-side variable names. The executor reads
write credentials only from GitHub Actions secrets and refuses to run outside Actions:
`ETSY_KEYSTRING`, `ETSY_WRITE_TOKEN`, `ETSY_SHOP_ID`, `PRINTIFY_WRITE_TOKEN`, `PRINTIFY_SHOP_ID`,
`PINTEREST_TOKEN`, `PAYHIP_API_KEY`. The image client also needs `IMAGE_API_URL` (not secret).
