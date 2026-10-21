# config/

| File | Purpose |
|---|---|
| `engine.yaml` | Ceilings the executor enforces (hours, listing counts, margin floors, ads caps, niche count). |
| `blocklist.yaml` | IP veto list used by `src/compliance/blocklist.py`, the executor and concept review. |

## Extending the blocklist

1. **Add a term** under the right category in `categories:`. Use lowercase. Terms match as whole
   words/phrases, case-insensitive (`"star wars"` matches "Star Wars mug", not "starwarsy").
2. **Add a category** by adding a new key under `categories:`. Every hit reports its category, so
   pick a name a reviewer will understand (e.g. `video_games`).
3. **Add a regex** under `regex:` when a plain term is not enough (lookalike spellings, hedging
   phrases like "inspired by", trademark symbols). Each entry needs a `name` and a `pattern`.
   Patterns are case-insensitive unless `case_sensitive: true`. Quote with single quotes in YAML.
4. **Test it.** Run `pytest tests/test_blocklist.py`. The test suite compiles every regex and
   checks each category is non-empty. Add a case to `tests/test_blocklist.py` for any new regex.
5. **Open a PR.** Blocklist changes are owner-approved like everything else. Never remove a term
   to unblock a specific listing; if a term is too broad, narrow it with a regex and note why.

When in doubt, block. A false positive costs one concept; a false negative can cost the shop.
