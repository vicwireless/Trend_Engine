import re

import pytest
import yaml

from src.compliance.blocklist import DEFAULT_PATH, Blocklist

REQUIRED = {"brands", "sports_leagues", "entertainment_franchises", "celebrities", "song_lyrics",
            "attributed_quotes", "universities", "military_insignia", "national_park_logos"}


@pytest.fixture(scope="module")
def bl():
    return Blocklist.load()


def test_all_categories_present_and_non_empty():
    data = yaml.safe_load(DEFAULT_PATH.read_text())
    assert REQUIRED <= set(data["categories"])
    assert all(data["categories"][c] for c in REQUIRED)


def test_every_regex_compiles():
    for entry in yaml.safe_load(DEFAULT_PATH.read_text())["regex"]:
        re.compile(entry["pattern"])


@pytest.mark.parametrize("text,category", [
    ("Star Wars inspired nursery print", "entertainment_franchises"),
    ("Kansas City NFL game day shirt", "sports_leagues"),
    ("Taylor Swift fan gift", "celebrities"),
    ("Harvard dorm poster", "universities"),
    ("USMC veteran gift", "military_insignia"),
    ("National Park Service arrowhead tee", "national_park_logos"),
    ("Keep Calm and Carry On print", "attributed_quotes"),
])
def test_category_hits(bl, text, category):
    assert category in {h.category for h in bl.check(text)}


@pytest.mark.parametrize("text,rule", [
    ("D1sney castle silhouette", "disney_lookalike"),
    ("Mug inspired by a famous wizard", "inspired_by_hedge"),
    ("Brand™ logo shirt", "trademark_symbols"),
    ("Swifties era tee", "swiftie"),
    ("Chiefs red kingdom", "team_mascot_city"),
    ('"Stay hungry, stay foolish" - Jobs', "quote_attribution"),
])
def test_regex_hits(bl, text, rule):
    assert rule in {h.rule for h in bl.check(text)}


@pytest.mark.parametrize("text", [
    "Minimalist pickleball court line art",
    "Cozy autumn apple pie recipe card",
    "Textured gouache mountain landscape",
    "Marvelous mom birthday card",
])
def test_clean_text_passes(bl, text):
    assert bl.check(text) == []


def test_checks_lists_of_tags(bl):
    assert bl.check(["fine", ["nested", "pokemon"]])
