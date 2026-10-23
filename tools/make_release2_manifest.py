"""Build releases/2026-10-23-release-2.yaml from assets/digital/2026-10-23-release-2 (draft listings only).

    PYTHONPATH=. python tools/make_release2_manifest.py
"""
from __future__ import annotations

from pathlib import Path

import yaml

from src.executor.hashing import file_sha256, payload_sha256
from tools.make_release_manifest import COMMON, DISCLOSURE, SNAPSHOT, TAXONOMY_PLANNER_TEMPLATES

ROOT = Path(__file__).resolve().parents[1]
ASSETS = "assets/digital/2026-10-23-release-2"
MANIFEST_ID = "2026-10-23-release-2"
PLN, HOL = "new-year-planners", "holiday-planners"

G = ["a4 planner", "letter planner", "instant download"]


def L(key, niche, price, title, tags, intro, get, alt, kind="pdf"):
    return dict(key=key, niche=niche, price=price, title=title, tags=tags, intro=intro, get=get, alt=alt, kind=kind)


LISTINGS = [
    L("monthly-planner", PLN, 6.99, "2027 Monthly Planner Printable, Month-at-a-Glance Calendar Pages, Letter and A4 PDF",
      ["2027 monthly planner", "monthly calendar", "2027 calendar", "printable planner", "planner pdf", "month at a glance", "minimal planner",
       "monthly layout", "goal planner", "new year planner", "calendar pages", *G[:2], ][:13],
      "A minimal 2027 monthly planner to print at home: twelve month spreads with a clear date grid, top goals and notes.",
      ["US Letter PDF, weeks start Sunday", "A4 PDF, weeks start Monday", "14 pages in each size: year-at-a-glance, 12 months, notes", "A how-to-print guide (PDF)"],
      "Monthly planner page with a seven-column date grid, top goals and notes"),
    L("daily-planner", PLN, 12.99, "2027 Daily Planner Printable, One Page Per Day, Hourly Schedule, Letter and A4 PDF",
      ["2027 daily planner", "daily planner", "day planner", "hourly planner", "planner pdf", "printable planner", "to do list", "daily schedule",
       "2027 planner", "productivity", "a4 planner", "letter planner", "new year gift"],
      "A 2027 daily planner to print at home: one page for every day of the year with an hourly schedule, top three priorities, to-dos and notes.",
      ["US Letter PDF", "A4 PDF", "365 daily pages in each size, 6 am to 9 pm schedule", "A how-to-print guide (PDF)"],
      "Daily planner page with hourly schedule, top three priorities and to-do list"),
    L("budget-planner", PLN, 6.99, "2027 Monthly Budget Planner Printable, Yearly Overview, Income and Expense Tracker PDF",
      ["budget planner", "2027 budget", "monthly budget", "finance planner", "expense tracker", "savings planner", "planner pdf",
       "budget printable", "money planner", "new year budget", "a4 planner", "letter planner", "instant download"],
      "A minimal 2027 budget planner to print at home: a yearly overview, twelve monthly budget pages and a year-in-review.",
      ["US Letter PDF", "A4 PDF", "14 pages in each size", "A how-to-print guide (PDF)"],
      "Monthly budget page with income, fixed expenses, everyday spending and savings tables"),
    L("meal-planner", PLN, 6.99, "2027 Weekly Meal Planner Printable, Grocery List, Breakfast Lunch Dinner Pages, PDF",
      ["meal planner", "weekly meal plan", "grocery list", "2027 meal planner", "menu planner", "meal prep", "planner pdf",
       "food planner", "family meal plan", "kitchen printable", "a4 planner", "letter planner", "instant download"],
      "A weekly meal planner to print at home: 53 weekly pages for 2027 with space for breakfast, lunch, dinner and snacks, plus a grocery list.",
      ["US Letter PDF", "A4 PDF", "54 pages in each size", "A how-to-print guide (PDF)"],
      "Weekly meal planner page with breakfast, lunch, dinner and snack columns"),
    L("cleaning-planner", PLN, 6.99, "Cleaning Planner Printable, Daily, Weekly and Monthly Cleaning Checklists, PDF",
      ["cleaning planner", "cleaning checklist", "house cleaning", "chore chart", "home planner", "cleaning schedule", "planner pdf",
       "weekly cleaning", "deep clean", "home organizer", "a4 planner", "letter planner", "instant download"],
      "A calm cleaning planner to print at home: a daily reset, weekly rotation, seven room checklists and twelve monthly deep-clean pages.",
      ["US Letter PDF", "A4 PDF", "22 pages in each size", "A how-to-print guide (PDF)"],
      "Cleaning planner page with daily and weekly checklists"),
    L("reading-log", PLN, 5.99, "2027 Reading Log Printable, Book Tracker, Want to Read List, Letter and A4 PDF",
      ["reading log", "book tracker", "2027 reading log", "reading journal", "book log", "reading challenge", "planner pdf",
       "book lover gift", "want to read", "printable log", "a4 planner", "letter planner", "instant download"],
      "A reading log to print at home: set a 2027 goal, log every book, keep a want-to-read list and pick your favorites.",
      ["US Letter PDF", "A4 PDF", "9 pages in each size, room for over 100 books", "A how-to-print guide (PDF)"],
      "Reading log page with title, author, dates, rating and notes columns"),
    L("fitness-log", PLN, 6.99, "2027 Fitness Log Printable, Monthly Workout Tracker, Goals and Check-ins, PDF",
      ["fitness log", "workout tracker", "workout log", "2027 fitness", "exercise log", "gym planner", "planner pdf",
       "fitness planner", "health tracker", "new year fitness", "a4 planner", "letter planner", "instant download"],
      "A fitness log to print at home: goals, a body check-in page and twelve monthly workout logs with minutes, effort and notes.",
      ["US Letter PDF", "A4 PDF", "14 pages in each size", "A how-to-print guide (PDF)"],
      "Monthly workout log page with a row for each day"),
    L("todo-project", PLN, 5.99, "To-Do List and Project Planner Printable, Undated Task Pages, Letter and A4 PDF",
      ["to do list", "project planner", "task planner", "undated planner", "checklist printable", "productivity planner", "planner pdf",
       "work planner", "weekly tasks", "goal planner", "a4 planner", "letter planner", "instant download"],
      "An undated to-do list and project planner to print at home as many times as you like.",
      ["US Letter PDF", "A4 PDF", "To-do and project pages, print as many copies as you need", "A how-to-print guide (PDF)"],
      "To-do list page with four sections and checkboxes"),
    L("gratitude-journal", PLN, 4.99, "Gratitude Journal Printable, Daily Gratitude Log, Undated Monthly Pages, Letter and A4 PDF",
      ["gratitude journal", "gratitude log", "daily gratitude", "self care planner", "mindfulness", "wellness journal", "planner pdf",
       "journal printable", "positive habits", "daily journal", "a4 planner", "letter planner", "instant download"],
      "A gratitude journal to print at home: an intentions page, twelve undated monthly logs for three good things a day, and a looking-back page.",
      ["US Letter PDF", "A4 PDF", "14 pages in each size, undated so you can start any month", "A how-to-print guide (PDF)"],
      "Gratitude log page with a row for each day of the month"),
    L("holiday-planner", HOL, 8.99, "2026 Christmas Planner Printable, Holiday Budget, Gift List, Card List, Countdown PDF",
      ["christmas planner", "holiday planner", "2026 christmas", "gift list", "holiday budget", "christmas printable", "planner pdf",
       "christmas countdown", "holiday organizer", "gift tracker", "a4 planner", "letter planner", "instant download"],
      "A Christmas and holiday planner to print at home: budget, gift and card lists, nine weekly countdown pages, meals, decorating and memories.",
      ["US Letter PDF", "A4 PDF", "19 pages in each size", "A how-to-print guide (PDF)"],
      "Holiday planner page with weekly countdown to-do list"),
    L("gift-tracker", HOL, 4.99, "Christmas Gift Tracker Printable, 2026 Gift List and Budget by Person, PDF",
      ["gift tracker", "christmas gift list", "gift list", "holiday budget", "christmas planner", "gift planner", "planner pdf",
       "shopping list", "christmas printable", "2026 christmas", "a4 planner", "letter planner", "instant download"],
      "A gift tracker to print at home: a budget by person, four tracker pages and a page for gift ideas.",
      ["US Letter PDF", "A4 PDF", "6 pages in each size", "A how-to-print guide (PDF)"],
      "Gift tracker page with columns for recipient, idea, store, price and status"),
    L("card-list", HOL, 3.99, "Holiday Card List Printable, Christmas Card Tracker, Sent and Received, PDF",
      ["christmas card list", "holiday card list", "card tracker", "address list", "christmas planner", "christmas printable", "planner pdf",
       "greeting cards", "2026 christmas", "holiday organizer", "a4 planner", "letter planner", "instant download"],
      "A holiday card list to print at home: four pages of 20 names with written, mailed and received columns.",
      ["US Letter PDF", "A4 PDF", "5 pages in each size", "A how-to-print guide (PDF)"],
      "Card list page with name, written, mailed, received and note columns"),
    L("holiday-meal", HOL, 4.99, "Holiday Meal Planner Printable, Christmas Menu, Cooking Timeline and Grocery List PDF",
      ["holiday meal planner", "christmas menu", "menu planner", "cooking timeline", "grocery list", "christmas dinner", "planner pdf",
       "thanksgiving planner", "meal planner", "holiday printable", "a4 planner", "letter planner", "instant download"],
      "A holiday meal planner to print at home: menu, cooking timeline and three grocery lists.",
      ["US Letter PDF", "A4 PDF", "5 pages in each size", "A how-to-print guide (PDF)"],
      "Holiday menu page with starters, mains, sides, desserts and drinks"),
    L("december-countdown", HOL, 3.99, "December Countdown Planner Printable, Dec 1 to 25 Daily Checklist, Letter and A4",
      ["christmas countdown", "december planner", "advent checklist", "countdown calendar", "christmas planner", "holiday traditions", "planner pdf",
       "christmas printable", "daily checklist", "2026 christmas", "a4 planner", "letter planner", "instant download"],
      "A December countdown planner to print at home: a daily checklist from Dec 1 to 25, four weekly plan pages and a traditions page.",
      ["US Letter PDF", "A4 PDF", "6 pages in each size", "A how-to-print guide (PDF)"],
      "December countdown page with a checklist for each day"),
    L("planner-bundle-2027", PLN, 19.99, "2027 Planner Bundle Printable, 11 Planners, Weekly, Monthly, Daily, Budget, Meal, PDF",
      ["planner bundle", "2027 planner", "printable bundle", "planner pdf", "daily planner", "weekly planner", "monthly planner",
       "budget planner", "meal planner", "habit tracker", "new year bundle", "a4 planner", "letter planner"],
      "Eleven 2027 printable planners in one download: weekly, monthly, daily, goal, habit, budget, meal, cleaning, reading, fitness and to-do.",
      ["Letter zip: 11 planner PDFs", "A4 zip: 11 planner PDFs", "A how-to-print guide (PDF)"],
      "Planner bundle preview showing six planner pages", kind="zip"),
    L("holiday-bundle-2026", HOL, 12.99, "Christmas and Holiday Bundle Printable, Planner, Gift Tracker, Card List, Meal Plan",
      ["christmas bundle", "holiday bundle", "christmas planner", "gift tracker", "card list", "meal planner", "christmas printable",
       "countdown planner", "planner pdf", "holiday organizer", "2026 christmas", "a4 planner", "letter planner"],
      "Five holiday printables in one download: Christmas planner, gift tracker, card list, holiday meal planner and December countdown.",
      ["Letter zip: 5 holiday PDFs", "A4 zip: 5 holiday PDFs", "A how-to-print guide (PDF)"],
      "Holiday bundle preview showing five holiday pages", kind="zip"),
]


def description(p):
    lines = [p["intro"], "", "WHAT YOU GET"] + [f"• {g}" for g in p["get"]]
    lines += ["", "Print at 100% / \"Actual size\". Matte cardstock or plain paper both work. It's mostly white space, so it's light on ink.", "", COMMON]
    return "\n".join(lines)


def op(name, niche, payload):
    return {"op": name, "niche": niche, "payload": payload, "payload_sha256": payload_sha256(payload)}


def main():
    ops = []
    for p in LISTINGS:
        assert len(p["tags"]) == 13 and len(set(p["tags"])) == 13 and all(len(t) <= 20 for t in p["tags"]), p["key"]
        assert len(p["title"].split()) <= 15, (p["key"], len(p["title"].split()))
        base = f"{ASSETS}/{p['key']}"
        n = p["niche"]
        idx = len(ops)
        ops.append(op("etsy_create_digital_listing", n, {
            "title": p["title"], "description": description(p), "tags": p["tags"], "taxonomy_id": TAXONOMY_PLANNER_TEMPLATES,
            "who_made": "i_did", "when_made": "2020_2026", "ai_assisted": True, "price_usd": p["price"],
            "cost_snapshot": SNAPSHOT, "cost_key": "digital"}))
        ref = f"$ref:ops[{idx}].listing_id"
        ext = "zip" if p["kind"] == "zip" else "pdf"
        for name in (f"{p['key']}-letter.{ext}", f"{p['key']}-a4.{ext}", f"{p['key']}-how-to-print.pdf"):
            ops.append(op("etsy_upload_file", n, {"listing_id": ref, "path": f"{base}/{name}",
                                                  "file_sha256": file_sha256(ROOT / base / name), "name": name}))
        for rank, kind in enumerate(["1-cover", "2-inside", "3-pages", "4-sizes", "5-print"], start=1):
            rel = f"{base}/images/{p['key']}-{kind}.png"
            ops.append(op("etsy_upload_image", n, {"listing_id": ref, "path": rel, "file_sha256": file_sha256(ROOT / rel), "rank": rank,
                                                   "alt_text": p["alt"] if rank in (1, 3) else f"{p['title'].split(',')[0]}: {kind.split('-', 1)[1]} image"}))
    manifest = {
        "manifest_id": MANIFEST_ID, "created_at": "2026-10-23T18:00:00Z", "created_by": "claude",
        "summary": "Release 2: 15 draft Etsy listings (9 more planners, 5 Christmas/holiday printables, 2 bundles) to reach the "
                   "20-listing Day 7 gate by 30 Oct. Drafts only; owner ticks the AI-generator field and publishes each.",
        "owner_minutes_estimate": 150, "ops": ops}
    out = ROOT / "releases" / f"{MANIFEST_ID}.yaml"
    out.write_text(yaml.safe_dump(manifest, sort_keys=False, width=120, allow_unicode=True), encoding="utf-8")
    print(out, len(ops), "ops")


if __name__ == "__main__":
    main()
