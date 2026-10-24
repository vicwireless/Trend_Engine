# data/inbox

Manual exports from tools with no usable API. Drop them in a dated folder; the sense step turns
them into signals with `python -m src.sense.signals --date YYYY-MM-DD`
(written to `data/signals/YYYY-MM-DD/<source>.json`, all labeled estimates).

| File | Where it comes from | Columns |
|---|---|---|
| `YYYY-MM-DD/erank_trendbuzz.csv` | eRank → Trends → Trend Buzz, Etsy, copy the table | `Keyword` (required), optional `Searches` |
| `YYYY-MM-DD/pinterest_trends.csv` | trends.pinterest.com, US, copy the table | `Trend` or `Keyword` (required), optional `Weekly change`, `Monthly change`, `Yearly change` |

CSV or tab-separated both work; the first row is the header. Keep the rows in the tool's order:
row order becomes `trend_rank`. Growth like `+120%` is stored as the ratio 1.2. A file without a
keyword column is rejected.
