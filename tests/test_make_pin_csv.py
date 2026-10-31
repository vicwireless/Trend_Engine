import csv
from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from tools import make_pin_csv as m

PIN = """## Pin {n}: {key}
- Image: `{img}`
- Board: {board}
- Title: {title}
- Description: Some description.
- Destination: https://www.etsy.com/listing/{lid} (swap in the Share & Save link)
"""


def write_md(tmp: Path, specs) -> Path:
    body = "# Pins\n\n" + "\n".join(PIN.format(n=i, key="k", img=img, board="B", title=t, lid=lid)
                                    for i, (img, t, lid) in enumerate(specs, 1))
    md = tmp / "pins.md"
    md.write_text(body)
    for img, _, _ in specs:
        (tmp / img).write_bytes(b"png")
    return md


def test_parse_and_variant_order(tmp_path):
    md = write_md(tmp_path, [("a1.png", "A one", 1), ("a2.png", "A two", 1), ("b1.png", "B one", 2)])
    pins = m.order_pins(m.parse_pins_md(md))
    assert [p.image.name for p in pins] == ["a1.png", "b1.png", "a2.png"]
    assert pins[0].link == "https://www.etsy.com/listing/1"


def test_schedule_rolls_late_slots_to_next_utc_day():
    t = m.schedule(5, date(2026, 11, 2), ["14:00", "17:00", "00:00", "02:00"])
    assert [x.strftime("%m-%d %H:%M") for x in t] == [
        "11-02 14:00", "11-02 17:00", "11-03 00:00", "11-03 02:00", "11-03 14:00"]
    assert t == sorted(t)


def test_csv_headers_urls_and_link_override(tmp_path):
    md = write_md(tmp_path, [("a1.png", "A one", 1)])
    pins = m.parse_pins_md(md)
    when = m.schedule(1, date(2026, 11, 2), ["14:00"])
    rows = m.build_rows(pins, when, tmp_path, {"1": "https://www.etsy.com/listing/1?share=x"})
    out = tmp_path / "out.csv"
    m.write_csv(rows, out)
    got = list(csv.DictReader(out.open()))
    assert list(got[0].keys()) == m.HEADERS
    assert got[0]["Media URL"] == m.RAW_BASE + "a1.png"
    assert got[0]["Publish date"] == "2026-11-02T14:00:00"
    assert got[0]["Link"].endswith("share=x")


@pytest.mark.parametrize("problem", ["missing_image", "past", "too_far", "long_title", "dup"])
def test_validate_fails_closed(tmp_path, problem):
    specs = [("a1.png", "A one", 1), ("a2.png", "A one" if problem == "dup" else "A two", 1)]
    md = write_md(tmp_path, specs)
    pins = m.parse_pins_md(md)
    now = datetime(2026, 10, 31, tzinfo=UTC)
    start = {"past": date(2026, 10, 1), "too_far": date(2026, 12, 15)}.get(problem, date(2026, 11, 2))
    when = m.schedule(len(pins), start, ["14:00"])
    if problem == "missing_image":
        pins[0].image.unlink()
    if problem == "long_title":
        pins[0].title = "x" * 101
    with pytest.raises(m.PinCsvError):
        m.validate(pins, when, now, tmp_path)


def test_bad_destination_rejected(tmp_path):
    md = tmp_path / "pins.md"
    md.write_text(PIN.format(n=1, key="k", img="a.png", board="B", title="T", lid="1")
                  .replace("https://www.etsy.com/listing/1", "https://example.com/x"))
    with pytest.raises(m.PinCsvError):
        m.parse_pins_md(md)


def test_repo_pin_files_parse():
    root = Path(__file__).resolve().parents[1]
    files = sorted(root.glob("assets/pins/*/pins.md"))
    pins = [p for f in files for p in m.parse_pins_md(f)]
    assert pins and all(p.image.is_file() for p in pins)
