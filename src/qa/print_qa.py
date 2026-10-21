"""Print-file QA. Fails closed: any failed check fails the file (CLAUDE.md rule 8).

Checks: pixel dimensions vs print size at the target ppi (300 by default), bleed, safe zone for
text layers, contrast ratio of text layers, sRGB profile, transparency where required, file size.

Usage:
    python -m src.qa.print_qa path/to/file.png spec.json
"""
from __future__ import annotations

import io
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageCms, ImageStat

Image.MAX_IMAGE_PIXELS = 400_000_000  # large print files are expected


@dataclass
class TextLayer:
    """A text region in pixel coordinates of the full canvas (including bleed).

    `fg` and `bg` are hex colors. If `bg` is omitted, the median color of the box is sampled.
    """
    name: str
    bbox: Sequence[int]  # left, top, right, bottom
    fg: str
    bg: str | None = None


@dataclass
class PrintSpec:
    width_in: float
    height_in: float
    ppi: int = 300
    bleed_in: float = 0.0
    safe_zone_in: float = 0.0
    require_transparency: bool = False
    max_file_mb: float = 20.0
    min_contrast: float = 4.5
    text_layers: list[TextLayer] = field(default_factory=list)

    @classmethod
    def from_dict(cls, d: dict) -> "PrintSpec":
        d = dict(d)
        d["text_layers"] = [TextLayer(**t) for t in d.get("text_layers", [])]
        return cls(**d)

    def required_px(self) -> tuple[int, int]:
        return (round((self.width_in + 2 * self.bleed_in) * self.ppi),
                round((self.height_in + 2 * self.bleed_in) * self.ppi))

    def safe_rect(self) -> tuple[int, int, int, int]:
        w, h = self.required_px()
        inset = round((self.bleed_in + self.safe_zone_in) * self.ppi)
        return inset, inset, w - inset, h - inset


@dataclass
class Check:
    name: str
    passed: bool
    detail: str


@dataclass
class QAReport:
    path: str
    checks: list[Check]

    @property
    def passed(self) -> bool:
        return all(c.passed for c in self.checks)

    def to_dict(self) -> dict:
        return {"path": self.path, "passed": self.passed, "checks": [asdict(c) for c in self.checks]}


def run(path: str | Path, spec: PrintSpec) -> QAReport:
    path = Path(path)
    checks: list[Check] = []
    with Image.open(path) as img:
        img.load()
        checks.append(_dimensions(img, spec))
        checks.append(_bleed(img, spec))
        checks.append(_safe_zone(spec))
        checks.extend(_contrast(img, spec))
        checks.append(_srgb(img))
        checks.append(_transparency(img, spec))
    checks.append(_file_size(path, spec))
    return QAReport(str(path), checks)


def _dimensions(img: Image.Image, spec: PrintSpec) -> Check:
    need_w, need_h = spec.required_px()
    w, h = img.size
    ok = w >= need_w and h >= need_h
    eff_ppi = min(w / (spec.width_in + 2 * spec.bleed_in), h / (spec.height_in + 2 * spec.bleed_in))
    return Check("dimensions", ok,
                 f"{w}x{h}px, need >= {need_w}x{need_h}px at {spec.ppi} ppi (effective {eff_ppi:.0f} ppi)")


def _bleed(img: Image.Image, spec: PrintSpec) -> Check:
    if spec.bleed_in == 0:
        return Check("bleed", True, "no bleed required")
    w, h = img.size
    need_w, need_h = spec.required_px()
    trim_w, trim_h = round(spec.width_in * spec.ppi), round(spec.height_in * spec.ppi)
    ok = w >= need_w and h >= need_h
    return Check("bleed", ok, f"{spec.bleed_in} in bleed each side: canvas {w}x{h}px vs "
                              f"{trim_w}x{trim_h}px trim, need {need_w}x{need_h}px")


def _safe_zone(spec: PrintSpec) -> Check:
    if not spec.text_layers:
        return Check("safe_zone", True, "no text layers declared")
    l, t, r, b = spec.safe_rect()
    outside = [tl.name for tl in spec.text_layers
               if tl.bbox[0] < l or tl.bbox[1] < t or tl.bbox[2] > r or tl.bbox[3] > b]
    return Check("safe_zone", not outside,
                 f"safe area {l},{t},{r},{b}" + (f"; outside: {', '.join(outside)}" if outside else ""))


def _contrast(img: Image.Image, spec: PrintSpec) -> list[Check]:
    out = []
    rgb = img.convert("RGB")
    for tl in spec.text_layers:
        fg = hex_to_rgb(tl.fg)
        if tl.bg:
            bg = hex_to_rgb(tl.bg)
        else:
            bg = tuple(int(v) for v in ImageStat.Stat(rgb.crop(tuple(tl.bbox))).median)
        ratio = contrast_ratio(fg, bg)
        out.append(Check(f"contrast:{tl.name}", ratio >= spec.min_contrast,
                         f"{ratio:.2f}:1 (min {spec.min_contrast}:1), fg {tl.fg} on bg {rgb_to_hex(bg)}"))
    return out


def _srgb(img: Image.Image) -> Check:
    if img.mode not in ("RGB", "RGBA"):
        return Check("srgb", False, f"mode {img.mode}; convert to RGB/RGBA with an sRGB profile")
    icc = img.info.get("icc_profile")
    if not icc:
        return Check("srgb", False, "no embedded ICC profile; embed sRGB")
    try:
        desc = ImageCms.getProfileDescription(ImageCms.ImageCmsProfile(io.BytesIO(icc)))
    except Exception as e:  # unreadable profile = fail closed
        return Check("srgb", False, f"unreadable ICC profile: {e}")
    return Check("srgb", "srgb" in desc.lower(), f"profile: {desc.strip()}")


def _transparency(img: Image.Image, spec: PrintSpec) -> Check:
    has_alpha = img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info)
    if not spec.require_transparency:
        return Check("transparency", True, "not required" + (" (has alpha)" if has_alpha else ""))
    if not has_alpha:
        return Check("transparency", False, f"mode {img.mode} has no alpha channel")
    lo, _ = img.convert("RGBA").getchannel("A").getextrema()
    return Check("transparency", lo < 255, "transparent pixels present" if lo < 255 else "alpha channel is fully opaque")


def _file_size(path: Path, spec: PrintSpec) -> Check:
    mb = path.stat().st_size / 1_000_000
    return Check("file_size", mb <= spec.max_file_mb, f"{mb:.2f} MB (max {spec.max_file_mb} MB)")


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_hex(c: Sequence[int]) -> str:
    return "#" + "".join(f"{int(v):02x}" for v in c[:3])


def relative_luminance(c: Sequence[int]) -> float:
    def ch(v: float) -> float:
        v /= 255
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    r, g, b = (ch(v) for v in c[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(a: Sequence[int], b: Sequence[int]) -> float:
    la, lb = sorted((relative_luminance(a), relative_luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print(__doc__)
        return 2
    spec = PrintSpec.from_dict(json.loads(Path(argv[1]).read_text()))
    report = run(argv[0], spec)
    print(json.dumps(report.to_dict(), indent=2))
    return 0 if report.passed else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
