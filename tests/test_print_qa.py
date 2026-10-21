import pytest
from PIL import Image, ImageCms, ImageDraw

from src.qa.print_qa import PrintSpec, TextLayer, contrast_ratio, run

SRGB = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()


def make(tmp_path, size, mode="RGB", color=(255, 255, 255), icc=SRGB, name="f.png", draw=None):
    img = Image.new(mode, size, color)
    if draw:
        draw(ImageDraw.Draw(img))
    path = tmp_path / name
    kw = {"icc_profile": icc} if icc else {}
    img.save(path, **kw)
    return path


def checks(report):
    return {c.name: c.passed for c in report.checks}


# 2x3 in at 300 ppi with 0.125 in bleed -> 675 x 975 px
SPEC = dict(width_in=2, height_in=3, ppi=300, bleed_in=0.125, safe_zone_in=0.125)


def test_good_file_passes(tmp_path):
    path = make(tmp_path, (675, 975), draw=lambda d: d.rectangle((100, 100, 300, 160), fill="black"))
    spec = PrintSpec(**SPEC, text_layers=[TextLayer("headline", (100, 100, 300, 160), fg="#ffffff", bg="#000000")])
    report = run(path, spec)
    assert report.passed, report.to_dict()


def test_low_resolution_fails(tmp_path):
    report = run(make(tmp_path, (600, 900)), PrintSpec(**SPEC))
    c = checks(report)
    assert not c["dimensions"] and not c["bleed"] and not report.passed


def test_text_outside_safe_zone_fails(tmp_path):
    spec = PrintSpec(**SPEC, text_layers=[TextLayer("edge", (10, 10, 200, 60), fg="#000000", bg="#ffffff")])
    assert not checks(run(make(tmp_path, (675, 975)), spec))["safe_zone"]


def test_low_contrast_fails_and_samples_background(tmp_path):
    path = make(tmp_path, (675, 975), color=(200, 200, 200))
    spec = PrintSpec(**SPEC, text_layers=[TextLayer("pale", (100, 100, 300, 160), fg="#bbbbbb")])
    report = run(path, spec)
    assert not checks(report)["contrast:pale"]
    assert "#c8c8c8" in next(c.detail for c in report.checks if c.name == "contrast:pale")


def test_missing_profile_fails(tmp_path):
    assert not checks(run(make(tmp_path, (675, 975), icc=None), PrintSpec(**SPEC)))["srgb"]


def test_cmyk_fails(tmp_path):
    path = make(tmp_path, (675, 975), mode="CMYK", color=(0, 0, 0, 0), icc=None, name="f.jpg")
    assert not checks(run(path, PrintSpec(**SPEC)))["srgb"]


def test_transparency_required(tmp_path):
    opaque = make(tmp_path, (675, 975), name="opaque.png")
    assert not checks(run(opaque, PrintSpec(**SPEC, require_transparency=True)))["transparency"]
    clear = make(tmp_path, (675, 975), mode="RGBA", color=(0, 0, 0, 0), name="clear.png")
    assert checks(run(clear, PrintSpec(**SPEC, require_transparency=True)))["transparency"]


def test_file_size_limit(tmp_path):
    path = make(tmp_path, (675, 975))
    assert not checks(run(path, PrintSpec(**SPEC, max_file_mb=0.000001)))["file_size"]


def test_contrast_ratio_reference_values():
    assert contrast_ratio((0, 0, 0), (255, 255, 255)) == pytest.approx(21.0)
    assert contrast_ratio((119, 119, 119), (255, 255, 255)) == pytest.approx(4.48, abs=0.01)
