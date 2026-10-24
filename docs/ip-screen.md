# IP screen

Every concept passes this screen before it is scored. Code: `src/compliance/ip_review.py`; the
result is the concept's `ip_review` record (`docs/data-model.md`). A veto sets `ip_veto`, which
zeroes the score (`docs/scoring.md`). Research behind it: the 2026-10-23 source review
(https://claude.ai/artifact/EhHEG5g4C6xYNgVbTaRbMR).

**Policy.** Ride a trend's sentiment, occasion or look with original wording and art. Never sell a
meme, a viral sound, a catchphrase tied to a person or show, or anything that names or evokes a
brand. Etsy acts on IP claims without investigating them, and a second strike can close the shop.

## Checks (all must pass; missing or `unknown` = veto)

| # | Check | How | Veto when |
|---|---|---|---|
| 1 | `blocklist` | Automatic: `config/blocklist.yaml` over phrase, title, tags and design text | Any hit |
| 2 | `origin` | Plain web search plus Know Your Meme "Origin" for the phrase or image | It comes from an identifiable person, show, song, game, team, brand, creator or named meme |
| 3 | `trademark` | USPTO trademark search (tmsearch.uspto.gov) for the exact phrase and its distinctive words, in the classes for the product (below). Record query and classes | Any live **or pending** mark in a covered class. A pending filing is enough for a takedown, even if the USPTO would later refuse it as a "widely used message" |
| 4 | `etsy_marketplace` | Etsy Open API search for the phrase | "Officially licensed" results, brand storefronts, or the top results are one rights holder's line |
| 5 | `text_copyright` | Read the text | Lyrics, poems, book or film lines, attributed quotes (CLAUDE.md rule 3). Short original phrases are fine: they are not copyrightable (US Copyright Office Circular 33) |
| 6 | `image_provenance` | Record the source of every image | Anything but our own generated art (flagged `ai_assisted`) or verified CC0/public domain with URL and object id. No meme templates, screenshots, reaction images or likenesses |
| 7 | record | Automatic | Each check stores `result`, `evidence` and `checked_at`. A pass with no evidence is a veto |

### Classes the trademark search must cover

| product_format | Nice classes |
|---|---|
| tshirt, sweatshirt, hoodie, hat | 025 |
| mug, tumbler | 021 |
| sticker, poster, art_print, card | 016 |
| tote_bag | 018 |
| pillow, blanket | 024 |
| printable_wall_art, planner, printable | 009, 016 |

An unlisted format is a veto until it is added here and in `CLASSES_BY_FORMAT`.

## Takedown notice

Deactivate the listing the same day, log it in `reports/incidents/YYYY-MM-DD-<slug>.md`, add the
term to the blocklist, and do not counter-notice without counsel.
