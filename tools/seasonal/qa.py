"""Print QA for the seasonal PDFs: rasterize every page at 300 ppi and run src/qa/print_qa.py on it.

    python -m tools.seasonal.qa --assets assets/digital/2026-11-15-seasonal --work <dir> --out reports/qa/2026-11-15-seasonal-print-qa.json

Checks per page: pixel size for the paper size at 300 ppi, sRGB profile, file size, and that the text
ink colors of the palette reach 4.5:1 on white inside a 0.25 in safe zone. Bundles are merges of pages
already checked in the singles plus their bonus pages, so they are checked in full as well.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path

from PIL import Image, ImageCms

from src.qa.print_qa import PrintSpec, TextLayer, run

from . import pages as P
from .build import ROOT
from .catalog import CATALOG

PAPER = {"us-letter": (8.5, 11.0), "a4": (8.27, 11.69)}
SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--assets", required=True)
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    work = Path(args.work) / "qa"
    work.mkdir(parents=True, exist_ok=True)
    report, failed = {"ppi": 300, "files": []}, 0
    for key, c in CATALOG.items():
        pal = P.PALETTES[c["palette"]]
        for size, (w_in, h_in) in PAPER.items():
            pdf = ROOT / args.assets / key / f"{key}-{size}.pdf"
            for old in work.glob("p-*.png"):
                old.unlink()
            subprocess.run(["pdftoppm", "-r", "300", "-png", str(pdf), str(work / "p")], check=True)
            pages = sorted(work.glob("p-*.png"))
            w_px, h_px = round(w_in * 300), round(h_in * 300)
            safe = round(0.25 * 300)
            box = [safe + 30, safe + 30, w_px - safe - 30, h_px - safe - 30]
            spec = PrintSpec(width_in=w_in, height_in=h_in, ppi=300, safe_zone_in=0.25, max_file_mb=20, text_layers=[
                TextLayer("body ink", box, pal["d"], "#ffffff"), TextLayer("headings", box, pal["a"], "#ffffff"),
                TextLayer("labels", box, pal["b"], "#ffffff"), TextLayer("body ink on tint", box, pal["d"], pal["p"]),
                TextLayer("headings on tint", box, pal["a"], pal["p"])])
            bad = []
            for i, png in enumerate(pages, 1):
                with Image.open(png) as im:
                    im.convert("RGB").save(png, icc_profile=SRGB, compress_level=1)
                r = run(png, spec)
                if not r.passed:
                    bad.append({"page": i, "failed": [f"{ch.name}: {ch.detail}" for ch in r.checks if not ch.passed]})
            failed += len(bad)
            entry = {"file": str(pdf.relative_to(ROOT)), "pages": len(pages), "pdf_mb": round(pdf.stat().st_size / 1e6, 2),
                     "passed": not bad and pdf.stat().st_size < 20e6, "failures": bad}
            report["files"].append(entry)
            print(entry["file"], entry["pages"], "PASS" if entry["passed"] else "FAIL", flush=True)
    report["passed"] = failed == 0
    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2) + "\n")
    print("ALL PASS" if failed == 0 else f"{failed} page(s) failed")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
