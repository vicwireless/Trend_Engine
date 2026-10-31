"""Build a Pinterest Bulk Create CSV from one or more pins.md files.

Pinterest's native Bulk Create (Create > Create Pin > Bulk create, business accounts) takes a CSV
of up to 200 rows and schedules each Pin at its publish date. Nothing here talks to Pinterest:
the owner uploads the file by hand, so this stays inside charter rule 1 (no external writes).

    python -m tools.make_pin_csv \
        --pins assets/pins/2026-10-23-release-2/pins.md assets/pins/2026-10-23/pins.md \
        --start 2026-11-02 --out assets/pins/csv/2026-11-02-bulk-create.csv

Media URLs point at raw.githubusercontent.com on main, so the images must be merged before
upload. Fails closed on any missing image, bad link, over-long text, or duplicate row.
"""
from __future__ import annotations

import argparse
import csv
import json
import re
import sys
from dataclasses import dataclass
from datetime import UTC, date, datetime, time, timedelta
from pathlib import Path

# Header order of Pinterest's Bulk Create template (verify against the template downloaded
# from the Bulk create screen before the first upload; Pinterest has no public schema page).
HEADERS = ["Title", "Media URL", "Pinterest board", "Thumbnail", "Description", "Link",
           "Publish date", "Keywords"]
RAW_BASE = "https://raw.githubusercontent.com/vicwireless/Trend_Engine/main/"
MAX_TITLE, MAX_DESC, MAX_ROWS, MAX_DAYS_AHEAD = 100, 500, 200, 30
# US evening/lunch peaks expressed in UTC (Eastern is UTC-5 after 2026-11-01).
DEFAULT_SLOTS = ["14:00", "17:00", "00:00", "02:00"]
LINK_RE = re.compile(r"^https://www\.etsy\.com/listing/(\d+)")


class PinCsvError(ValueError):
    pass


@dataclass
class Pin:
    source: Path
    image: Path
    board: str
    title: str
    description: str
    link: str
    listing_id: str
    variant: int = 0  # 0 = first pin for this listing in its file, 1 = second, ...


def parse_pins_md(path: Path) -> list[Pin]:
    text = path.read_text(encoding="utf-8")
    pins: list[Pin] = []
    seen: dict[str, int] = {}
    for block in re.split(r"^## ", text, flags=re.MULTILINE)[1:]:
        fields = dict(re.findall(r"^- (Image|Board|Title|Description|Destination): (.+)$", block, flags=re.MULTILINE))
        missing = {"Image", "Board", "Title", "Description", "Destination"} - fields.keys()
        if missing:
            raise PinCsvError(f"{path}: pin '{block.splitlines()[0]}' missing {sorted(missing)}")
        link = fields["Destination"].split(" (")[0].strip()
        m = LINK_RE.match(link)
        if not m:
            raise PinCsvError(f"{path}: destination is not an Etsy listing URL: {link}")
        lid = m.group(1)
        variant = seen.get(lid, 0)
        seen[lid] = variant + 1
        pins.append(Pin(path, path.parent / fields["Image"].strip("` "), fields["Board"].strip(),
                        fields["Title"].strip(), fields["Description"].strip(), link, lid, variant))
    return pins


def order_pins(pins: list[Pin]) -> list[Pin]:
    """First variant of every listing in input order, then second variants, and so on.

    Keeps the same destination off consecutive slots, and the input order sets priority
    (pass the Christmas file first: its buying window closes soonest)."""
    return sorted(pins, key=lambda p: p.variant)  # stable sort keeps file/input order


def schedule(n: int, start: date, slots: list[str]) -> list[datetime]:
    times = [time.fromisoformat(s) for s in slots]
    out, day = [], start
    while len(out) < n:
        for i, t in enumerate(times):
            # Slots earlier than the first one roll into the next UTC day (US evening).
            d = day + timedelta(days=1) if i and t < times[0] else day
            out.append(datetime.combine(d, t, tzinfo=UTC))
            if len(out) == n:
                break
        day += timedelta(days=1)
    return out


def validate(pins: list[Pin], when: list[datetime], now: datetime, repo_root: Path) -> None:
    if len(pins) > MAX_ROWS:
        raise PinCsvError(f"{len(pins)} rows; Pinterest bulk create takes at most {MAX_ROWS}")
    seen_img, seen_title = set(), set()
    for p, t in zip(pins, when):
        if not p.image.is_file():
            raise PinCsvError(f"image not found: {p.image}")
        try:
            p.image.resolve().relative_to(repo_root.resolve())
        except ValueError as e:
            raise PinCsvError(f"image is outside the repo, so it has no public URL: {p.image}") from e
        if len(p.title) > MAX_TITLE:
            raise PinCsvError(f"title over {MAX_TITLE} chars: {p.title}")
        if len(p.description) > MAX_DESC:
            raise PinCsvError(f"description over {MAX_DESC} chars: {p.title}")
        if p.image in seen_img or p.title in seen_title:
            raise PinCsvError(f"duplicate pin: {p.image.name} / {p.title}")
        seen_img.add(p.image)
        seen_title.add(p.title)
        if t <= now:
            raise PinCsvError(f"publish date {t.isoformat()} is not in the future")
        if t > now + timedelta(days=MAX_DAYS_AHEAD):
            raise PinCsvError(f"publish date {t.isoformat()} is more than {MAX_DAYS_AHEAD} days ahead")


def build_rows(pins: list[Pin], when: list[datetime], repo_root: Path,
               links: dict[str, str]) -> list[dict[str, str]]:
    rows = []
    for p, t in zip(pins, when):
        rel = p.image.resolve().relative_to(repo_root.resolve()).as_posix()
        rows.append({
            "Title": p.title,
            "Media URL": RAW_BASE + rel,
            "Pinterest board": p.board,
            "Thumbnail": "",
            "Description": p.description,
            "Link": links.get(p.listing_id, p.link),
            "Publish date": t.strftime("%Y-%m-%dT%H:%M:%S"),
            "Keywords": "",
        })
    return rows


def write_csv(rows: list[dict[str, str]], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=HEADERS)
        w.writeheader()
        w.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--pins", nargs="+", type=Path, required=True, help="pins.md files, priority order")
    ap.add_argument("--start", type=date.fromisoformat, required=True, help="first publish day (UTC)")
    ap.add_argument("--slots", default=",".join(DEFAULT_SLOTS), help="UTC HH:MM times per day")
    ap.add_argument("--skip", nargs="*", default=[], help="image file names already posted by hand")
    ap.add_argument("--links", type=Path, help="JSON {listing_id: share_and_save_url} overrides")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--repo-root", type=Path, default=Path("."))
    a = ap.parse_args(argv)

    pins = [p for f in a.pins for p in parse_pins_md(f) if p.image.name not in set(a.skip)]
    pins = order_pins(pins)
    when = schedule(len(pins), a.start, [s.strip() for s in a.slots.split(",") if s.strip()])
    links = json.loads(a.links.read_text()) if a.links else {}
    try:
        validate(pins, when, datetime.now(UTC), a.repo_root)
    except PinCsvError as e:
        print(f"STOP: {e}", file=sys.stderr)
        return 2
    write_csv(build_rows(pins, when, a.repo_root, links), a.out)
    print(f"{len(pins)} pins, {when[0]:%Y-%m-%d %H:%M} to {when[-1]:%Y-%m-%d %H:%M} UTC -> {a.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
