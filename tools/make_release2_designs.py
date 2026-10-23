"""Generate release 2 printables: more 2027 planners, the 2026 holiday set, bundles, and their listing images.

    PYTHONPATH=. python tools/make_release2_designs.py --out assets/digital/2026-10-23-release-2

Original code-drawn layouts only (same system as make_planner_family.py). Per product: Letter and A4 PDFs,
a one-page print guide and five 2400x1800 listing images. Bundles are zips of the member PDFs.
"""
from __future__ import annotations

import argparse
import calendar
import datetime as dt
import zipfile
from pathlib import Path

from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas

from tools.make_planner_family import (INK, MARGIN, MONTHS, MUTED, RULE, SAGE, SIZES, YEAR, box, footer, guide,
                                       header, images, lined, week_start)

HOLIDAY_YEAR = 2026


# ---------------------------------------------------------------- building blocks
def draw_table(c, x0, top, tw, cols, nrows, rh, first_labels=None):
    tot = sum(r for _, r in cols)
    xs = [x0]
    for _, r in cols:
        xs.append(xs[-1] + tw * r / tot)
    c.setFont("Sans-Bold", 7.5)
    c.setFillColor(SAGE)
    for i, (lab, _) in enumerate(cols):
        c.drawString(xs[i] + 4, top - 12, lab.upper())
    t = top - 18
    c.setStrokeColor(RULE)
    c.setLineWidth(0.6)
    for r in range(nrows + 1):
        c.line(x0, t - r * rh, x0 + tw, t - r * rh)
    for xv in xs:
        c.line(xv, t, xv, t - nrows * rh)
    if first_labels:
        c.setFont("Sans", 8.5)
        c.setFillColor(INK)
        for r, lab in enumerate(first_labels[:nrows]):
            c.drawString(x0 + 4, t - (r + 1) * rh + rh / 2 - 3, lab)
    return t - nrows * rh


def table_page(title, sub, cols, nrows, first_labels=None, max_rh=36):
    def pg(c, w, h, size, label):
        y = header(c, w, h, title, sub)
        rh = min(max_rh, (y - 70) / nrows)
        draw_table(c, MARGIN, y - 4, w - 2 * MARGIN, cols, nrows, rh, first_labels)
        footer(c, w, label)
    return pg


def stack_page(title, sub, items):
    """items: (label, weight). Stacked boxes with writing lines."""
    def pg(c, w, h, size, label):
        y = header(c, w, h, title, sub)
        total = sum(wt for _, wt in items)
        avail = y - 60
        for lab, wt in items:
            bh = avail * wt / total
            box(c, MARGIN, y - bh + 8, w - 2 * MARGIN, bh - 8, lab)
            lined(c, MARGIN + 10, y - 6, w - 2 * MARGIN - 20, int((bh - 34) // 20), 20)
            y -= bh
        footer(c, w, label)
    return pg


def check_page(title, sub, groups):
    """groups: (heading, [items]) laid out in two columns; blank lines pad each group."""
    def pg(c, w, h, size, label):
        y = header(c, w, h, title, sub)
        colw = (w - 2 * MARGIN - 20) / 2
        pos = [y - 6, y - 6]
        for i, (head, items) in enumerate(groups):
            col = i % 2
            x = MARGIN + col * (colw + 20)
            yy = pos[col]
            c.setFont("Serif-Bold", 12)
            c.setFillColor(INK)
            c.drawString(x, yy - 12, head)
            yy -= 24
            for it in items:
                c.setStrokeColor(RULE)
                c.rect(x, yy - 10, 9, 9, stroke=1, fill=0)
                c.setFont("Sans", 9.5)
                c.setFillColor(INK)
                if it:
                    c.drawString(x + 15, yy - 9, it)
                else:
                    c.line(x + 15, yy - 10, x + colw, yy - 10)
                yy -= 19
            pos[col] = yy - 12
        footer(c, w, label)
    return pg


def month_page(m):
    def pg(c, w, h, size, label):
        y = header(c, w, h, MONTHS[m - 1], f"{YEAR} monthly planner")
        names = [calendar.day_abbr[(week_start(size) + i) % 7] for i in range(7)]
        cw = (w - 2 * MARGIN) / 7
        weeks = calendar.Calendar(week_start(size)).monthdayscalendar(YEAR, m)
        grid_h = (y - 150) * 1.0
        rh = grid_h / 6
        c.setFont("Sans-Bold", 8)
        c.setFillColor(SAGE)
        for i, n in enumerate(names):
            c.drawCentredString(MARGIN + (i + 0.5) * cw, y - 14, n.upper())
        top = y - 22
        c.setStrokeColor(RULE)
        c.setLineWidth(0.6)
        for r in range(7):
            c.line(MARGIN, top - r * rh, w - MARGIN, top - r * rh)
        for i in range(8):
            c.line(MARGIN + i * cw, top, MARGIN + i * cw, top - 6 * rh)
        for r, wk in enumerate(weeks):
            for i, d in enumerate(wk):
                if d:
                    c.setFont("Sans-Bold", 9)
                    c.setFillColor(INK)
                    c.drawString(MARGIN + i * cw + 4, top - r * rh - 12, str(d))
        by = top - 6 * rh - 14
        half = (w - 2 * MARGIN - 14) / 2
        box(c, MARGIN, 44, half, by - 44, "Top goals this month")
        lined(c, MARGIN + 8, by - 8, half - 16, int((by - 44 - 18) // 18), 18)
        box(c, MARGIN + half + 14, 44, half, by - 44, "Notes")
        lined(c, MARGIN + half + 22, by - 8, half - 16, int((by - 44 - 18) // 18), 18)
        footer(c, w, label)
    return pg


def day_page(d):
    def pg(c, w, h, size, label):
        y = header(c, w, h, f"{calendar.day_name[d.weekday()]}, {d:%B} {d.day}", f"{d.year}  |  day {d.timetuple().tm_yday}")
        left = (w - 2 * MARGIN) * 0.55
        rx = MARGIN + left + 14
        rw = w - MARGIN - rx
        top = y - 6
        hours = list(range(6, 22))
        rh = (top - 60) / len(hours)
        c.setStrokeColor(RULE)
        c.setLineWidth(0.5)
        c.setFont("Sans", 8)
        c.setFillColor(MUTED)
        for i, hr in enumerate(hours):
            yy = top - (i + 1) * rh
            c.line(MARGIN + 34, yy, MARGIN + left, yy)
            c.drawString(MARGIN, yy + 3, f"{(hr - 1) % 12 + 1} {'am' if hr < 12 else 'pm'}")
        ph = (top - 60) * 0.22
        box(c, rx, top - ph, rw, ph, "Top 3 priorities")
        for i in range(3):
            c.rect(rx + 8, top - 34 - i * 22, 9, 9, stroke=1, fill=0)
            c.line(rx + 24, top - 34 - i * 22, rx + rw - 8, top - 34 - i * 22)
        th = (top - 60) * 0.42
        ty = top - ph - 10
        box(c, rx, ty - th, rw, th, "To do")
        for i in range(int((th - 20) // 20)):
            c.rect(rx + 8, ty - 32 - i * 20, 9, 9, stroke=1, fill=0)
            c.line(rx + 24, ty - 32 - i * 20, rx + rw - 8, ty - 32 - i * 20)
        ny = ty - th - 10
        nh = ny - 60
        box(c, rx, 60, rw, nh, "Notes")
        lined(c, rx + 8, ny - 14, rw - 16, int((nh - 18) // 20), 20)
        footer(c, w, label)
    return pg


def week_rows_page(start_fn, n, title_fn, sub_fn, cols, first_fn):
    """n weekly pages; start_fn(size) gives the first week's start date."""
    pages = []
    for i in range(n):
        def pg(c, w, h, size, label, i=i):
            d = start_fn(size) + dt.timedelta(days=7 * i)
            y = header(c, w, h, title_fn(i, d), sub_fn(i, d))
            labels = [f"{calendar.day_abbr[(d + dt.timedelta(days=k)).weekday()]} {(d + dt.timedelta(days=k)):%b} {(d + dt.timedelta(days=k)).day}"
                      for k in range(7)]
            rh = min(60, (y - 76) / 7)
            draw_table(c, MARGIN, y - 4, w - 2 * MARGIN, cols, 7, rh, labels)
            footer(c, w, label)
        pages.append(pg)
    return pages


def week_start_on_or_before(day: dt.date, size: str) -> dt.date:
    first = week_start(size)
    d = day
    while d.weekday() != (6 if first == calendar.SUNDAY else 0):
        d -= dt.timedelta(days=1)
    return d


def year_weeks(size):
    return week_start_on_or_before(dt.date(YEAR, 1, 1), size)


def holiday_weeks(size):
    return week_start_on_or_before(dt.date(HOLIDAY_YEAR, 11, 1), size)


def cover_free(title, sub):
    return stack_page(title, sub, [("Notes", 1)])


# ---------------------------------------------------------------- page sets
def budget_month(m):
    def pg(c, w, h, size, label):
        y = header(c, w, h, MONTHS[m - 1], f"{YEAR} monthly budget")
        tw = w - 2 * MARGIN
        cols = [("Item", 3), ("Planned", 1.2), ("Actual", 1.2)]
        yy = y - 2
        for lab, n in [("Income", 4), ("Fixed expenses", 8), ("Everyday spending", 7), ("Savings and debt", 4)]:
            c.setFont("Serif-Bold", 11)
            c.setFillColor(INK)
            c.drawString(MARGIN, yy - 10, lab)
            rh = 18
            yy = draw_table(c, MARGIN, yy - 12, tw, cols, n, rh) - 8
        box(c, MARGIN, 44, tw, yy - 44, "What I will change next month")
        footer(c, w, label)
    return pg


def pages_monthly():
    return ([cover_free(f"{YEAR} At a Glance", "Dates to remember")] + [month_page(m) for m in range(1, 13)]
            + [cover_free("Notes", "")])


def pages_daily():
    d0 = dt.date(YEAR, 1, 1)
    return [day_page(d0 + dt.timedelta(days=i)) for i in range(365)]


def pages_budget():
    return ([table_page(f"{YEAR} Budget Overview", "Set the targets for the year",
                        [("Category", 3), ("Monthly target", 1.5), ("Yearly target", 1.5)], 16)]
            + [budget_month(m) for m in range(1, 13)]
            + [table_page("Year in Review", "Total saved and spent",
                          [("Month", 2), ("Income", 1.5), ("Spent", 1.5), ("Saved", 1.5)], 12,
                          first_labels=MONTHS)])


def pages_meal():
    cols = [("Day", 1.4), ("Breakfast", 2), ("Lunch", 2), ("Dinner", 2.4), ("Snack", 1.4)]
    pages = week_rows_page(year_weeks, 53, lambda i, d: f"Week {i + 1}", lambda i, d: f"{YEAR} meal plan", cols, None)
    return pages + [stack_page("Grocery List", "Print extra copies", [("Produce", 1), ("Pantry and dry goods", 1),
                                                                       ("Dairy and fridge", 1), ("Frozen and other", 1)])]


def pages_cleaning():
    rooms = ["Kitchen", "Bathroom", "Bedroom", "Living room", "Entry", "Laundry", "Office"]
    daily = check_page("Daily Reset", "Ten minutes a day keeps it calm",
                       [("Morning", ["Make the bed", "Open the blinds", "Load or empty the dishwasher", "Wipe the counters", ""]),
                        ("Evening", ["Tidy the living room", "Dishes done", "Quick floor sweep", "Set out tomorrow's things", ""])])
    weekly = table_page("Weekly Cleaning Rotation", "One focus per day",
                        [("Day", 1.4), ("Focus", 2), ("Tasks", 4), ("Done", 0.8)], 7,
                        first_labels=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])
    room_pages = [check_page(r, "Room checklist", [("Weekly", ["Dust surfaces", "Vacuum or sweep", "Wipe handles and switches", "Empty bins", ""]),
                                                  ("Monthly", ["Wash windows or mirrors", "Clean under furniture", "Wipe baseboards", "Sort and donate", ""])])
                  for r in rooms]
    months = [check_page(f"{MONTHS[m]} Deep Clean", f"{YEAR} monthly deep clean",
                         [("This month", ["", "", "", "", "", ""]), ("Notes", ["", "", "", ""])]) for m in range(12)]
    supplies = stack_page("Supplies List", "Restock when low", [("Cleaning products", 1), ("Tools and cloths", 1), ("To buy", 1)])
    return [daily, weekly] + room_pages + months + [supplies]


def pages_reading():
    cols = [("Title", 3), ("Author", 2), ("Started", 1), ("Finished", 1), ("Rating", 1), ("Notes", 2.2)]
    goal = stack_page(f"{YEAR} Reading Goals", "Books, genres and habits",
                      [("My reading goal", 1), ("Books I want to read", 2), ("Genres I want to try", 1)])
    return ([goal] + [table_page(f"Reading Log {i + 1}", f"{YEAR}", cols, 18) for i in range(6)]
            + [table_page("Want to Read", "A running list", [("Title", 3), ("Author", 2), ("Why", 3)], 22),
               stack_page("Favorite Books of the Year", "Looking back", [("Top five", 1), ("What I learned", 1)])])


def pages_fitness():
    cols = [("Date", 1.2), ("Workout", 3), ("Minutes", 1), ("Effort 1-5", 1), ("Notes", 3)]
    pages = [stack_page(f"{YEAR} Fitness Goals", "Where I am and where I want to be",
                        [("My goals", 2), ("Why they matter", 1), ("Starting point", 1)]),
             table_page("Body Check-ins", "Optional: measure monthly",
                        [("Month", 1.5), ("Weight", 1), ("Waist", 1), ("Energy 1-5", 1), ("Notes", 3)], 12, first_labels=MONTHS)]
    for m in range(1, 13):
        n = calendar.monthrange(YEAR, m)[1]
        labels = [f"{calendar.day_abbr[dt.date(YEAR, m, d).weekday()]} {d}" for d in range(1, n + 1)]
        pages.append(table_page(MONTHS[m - 1], f"{YEAR} workout log", cols, n, first_labels=labels))
    return pages


def pages_todo():
    todo = check_page("To-Do List", "Pick three that matter most",
                      [("Today", [""] * 9), ("This week", [""] * 9), ("Soon", [""] * 9), ("Waiting on", [""] * 9)])
    project = stack_page("Project Planner", "Goal, steps, deadlines",
                         [("Project and why it matters", 1), ("Steps", 2), ("Deadlines and owners", 1), ("Notes", 1)])
    return [todo] * 12 + [project] * 6


def pages_gratitude():
    month = table_page("Gratitude Log", "Three good things a day",
                       [("Day", 1), ("I am grateful for", 4), ("Small win", 3)], 31, first_labels=[str(d) for d in range(1, 32)], max_rh=24)
    return [stack_page("My Gratitude Intentions", "Why I am starting", [("What I want to notice more", 1), ("People I appreciate", 1)])] + [month] * 12 + [
        stack_page("Looking Back", "A year of good things", [("Moments I loved", 1), ("What I learned", 1)])]


def pages_holiday():
    ws = holiday_weeks
    weeks = week_rows_page(ws, 9, lambda i, d: f"Week of {d:%b} {d.day}", lambda i, d: f"{HOLIDAY_YEAR} holiday countdown",
                           [("Day", 1.4), ("To do", 5), ("Done", 0.8)], None)
    gifts = [table_page(f"Gift List {i + 1}", f"{HOLIDAY_YEAR}", [("For", 2), ("Gift idea", 3), ("Budget", 1), ("Spent", 1),
                                                                   ("Bought", 0.8), ("Wrapped", 0.8)], 18) for i in range(3)]
    cards = [table_page(f"Card List {i + 1}", "Who gets one", [("Name", 3), ("Sent", 1), ("Received", 1), ("Note", 3)], 20) for i in range(2)]
    return ([stack_page(f"{HOLIDAY_YEAR} Holiday Overview", "Dates, traditions, and what matters",
                        [("Key dates", 2), ("Traditions I want to keep", 2), ("What I will skip this year", 1)]),
             table_page("Holiday Budget", "Know the number before you shop",
                        [("Category", 3), ("Budget", 1.5), ("Spent", 1.5), ("Left", 1.5)], 12,
                        first_labels=["Gifts", "Food", "Decor", "Cards and postage", "Travel", "Wrapping", "Entertaining", "Charity",
                                      "Clothing", "Other", "Other", "Total"])]
            + gifts + cards + weeks
            + [check_page("Shopping and Decorating", "Tick as you go",
                          [("Shopping", [""] * 8), ("Decorating", ["Tree or greenery", "Lights", "Table", "Front door", "", "", "", ""])]),
               stack_page("Holiday Meal Plan", "Menu and timing", [("Menu", 2), ("Shopping list", 2), ("Cooking timeline", 2)]),
               stack_page("Memories", "Write them down before they blur", [("Favorite moments", 2), ("Photos to print", 1), ("Next year", 1)])])


def pages_gifttracker():
    gifts = [table_page(f"Gift Tracker {i + 1}", f"{HOLIDAY_YEAR}", [("For", 2), ("Idea", 3), ("Where", 1.5), ("Price", 1), ("Status", 1.2)], 18)
             for i in range(4)]
    return [table_page("Gift Budget", "Set a limit per person", [("Person", 3), ("Budget", 1.5), ("Spent", 1.5)], 16)] + gifts + [
        stack_page("Wish Ideas", "Things people mention", [("Overheard ideas", 2), ("Gift closet inventory", 1)])]


def pages_cards():
    return ([table_page(f"Holiday Card List {i + 1}", f"{HOLIDAY_YEAR}", [("Name", 3), ("Written", 1), ("Mailed", 1), ("Received", 1), ("Note", 3)], 20)
             for i in range(4)] + [stack_page("Card Notes", "Messages and reminders", [("Messages", 1), ("Reminders", 1)])])


def pages_holidaymeal():
    return ([stack_page("Holiday Menu", f"{HOLIDAY_YEAR}", [("Starters", 1), ("Mains", 1), ("Sides", 1), ("Desserts", 1), ("Drinks", 1)]),
             stack_page("Cooking Timeline", "Work backward from serving time", [("Days before", 1), ("Day before", 1), ("Day of", 2)])]
            + [stack_page(f"Grocery List {i + 1}", "Print extra copies", [("Produce", 1), ("Pantry", 1), ("Dairy and fridge", 1), ("Other", 1)])
               for i in range(3)])


def pages_countdown():
    days = [str(d) for d in range(1, 26)]
    first = table_page("December Countdown", "A small thing each day", [("Day", 1), ("Something to do", 6), ("Done", 1)], 25,
                       first_labels=[f"Dec {d}" for d in days], max_rh=24)
    wk = [stack_page(f"Countdown Week {i + 1}", "Plans and reminders", [("Plans", 2), ("Reminders", 1)]) for i in range(4)]
    return [first] + wk + [stack_page("Traditions", "Write down what you did", [("This year", 1), ("Next year", 1)])]


# ---------------------------------------------------------------- products
# key -> dict(title, year, tagline, inside, pages fn, week_note)
PRODUCTS = {
    "monthly-planner": dict(
        title="Monthly Planner Printable", year=str(YEAR), tagline="Twelve month spreads with goals and notes.",
        inside=["Twelve month-at-a-glance calendars", "Top goals and notes on every month", "Year-at-a-glance page", "How-to-print guide"],
        pages=pages_monthly, week_note=True),
    "daily-planner": dict(
        title="Daily Planner Printable", year=str(YEAR), tagline="One page a day, hour by hour.",
        inside=["365 daily pages for 2027", "Hourly schedule from 6 am to 9 pm", "Top 3 priorities, to-do list and notes", "How-to-print guide"],
        pages=pages_daily, week_note=False),
    "budget-planner": dict(
        title="Monthly Budget Planner Printable", year=str(YEAR), tagline="Plan every month and see the whole year.",
        inside=["Yearly budget overview", "Twelve monthly budget pages", "Income, fixed, everyday and savings tables", "Year-in-review page", "How-to-print guide"],
        pages=pages_budget, week_note=False),
    "meal-planner": dict(
        title="Weekly Meal Planner Printable", year=str(YEAR), tagline="Plan the week and shop once.",
        inside=["53 weekly meal planning pages", "Breakfast, lunch, dinner and snack for each day", "Printable grocery list page", "How-to-print guide"],
        pages=pages_meal, week_note=True),
    "cleaning-planner": dict(
        title="Cleaning Planner Printable", year=str(YEAR), tagline="A calm routine for every room.",
        inside=["Daily reset and weekly rotation", "Seven room checklists", "Twelve monthly deep clean pages", "Supplies list and how-to-print guide"],
        pages=pages_cleaning, week_note=False),
    "reading-log": dict(
        title="Reading Log Printable", year=str(YEAR), tagline="Track every book you read this year.",
        inside=["Reading goals page", "Six log pages with room for over 100 books", "Want-to-read list", "Favorites of the year", "How-to-print guide"],
        pages=pages_reading, week_note=False),
    "fitness-log": dict(
        title="Fitness Log Printable", year=str(YEAR), tagline="Twelve monthly workout logs.",
        inside=["Fitness goals page", "Body check-in page", "Twelve monthly workout logs", "Workout, minutes, effort and notes columns", "How-to-print guide"],
        pages=pages_fitness, week_note=False),
    "todo-project": dict(
        title="To-Do List and Project Planner Printable", year="TO-DO", tagline="Undated lists you can reprint forever.",
        inside=["Undated to-do list page with four sections", "Project planner page", "Print as many copies as you need", "How-to-print guide"],
        pages=pages_todo, week_note=False),
    "gratitude-journal": dict(
        title="Gratitude Journal Printable", year="DAILY", tagline="Three good things a day.",
        inside=["Intentions page", "Twelve undated monthly gratitude logs", "Looking-back page", "How-to-print guide"],
        pages=pages_gratitude, week_note=False),
    "holiday-planner": dict(
        title="Christmas and Holiday Planner Printable", year=str(HOLIDAY_YEAR), tagline="Budget, gifts, cards, meals and a weekly countdown.",
        inside=["Overview and holiday budget", "Gift lists and card lists", "Nine weekly countdown pages from November", "Meal plan, shopping and decorating checklists", "Memory page and how-to-print guide"],
        pages=pages_holiday, week_note=True),
    "gift-tracker": dict(
        title="Christmas Gift Tracker Printable", year=str(HOLIDAY_YEAR), tagline="Who, what, where and how much.",
        inside=["Gift budget by person", "Four gift tracker pages", "Wish ideas page", "How-to-print guide"],
        pages=pages_gifttracker, week_note=False),
    "card-list": dict(
        title="Holiday Card List Printable", year=str(HOLIDAY_YEAR), tagline="Written, mailed, received.",
        inside=["Four card list pages with 20 names each", "Written, mailed and received columns", "Notes page", "How-to-print guide"],
        pages=pages_cards, week_note=False),
    "holiday-meal": dict(
        title="Holiday Meal Planner Printable", year=str(HOLIDAY_YEAR), tagline="Menu, timeline and grocery lists.",
        inside=["Holiday menu page", "Cooking timeline", "Three grocery list pages", "How-to-print guide"],
        pages=pages_holidaymeal, week_note=False),
    "december-countdown": dict(
        title="December Countdown Planner Printable", year="DEC", tagline="A small thing to do each day.",
        inside=["Dec 1 to 25 countdown checklist", "Four weekly plan pages", "Traditions page", "How-to-print guide"],
        pages=pages_countdown, week_note=False),
}

BUNDLES = {
    "planner-bundle-2027": dict(
        title="Planner Bundle Printable", year=str(YEAR), tagline="Ten printable planners in one download.",
        members=["monthly-planner", "daily-planner", "budget-planner", "meal-planner", "cleaning-planner", "reading-log", "fitness-log", "todo-project"],
        extra_existing=["weekly-planner", "goal-planner", "habit-tracker"], preview=["monthly-planner", "daily-planner", "budget-planner", "meal-planner", "cleaning-planner", "reading-log"]),
    "holiday-bundle-2026": dict(
        title="Christmas and Holiday Bundle Printable", year=str(HOLIDAY_YEAR), tagline="Five holiday planners in one download.",
        members=["holiday-planner", "gift-tracker", "card-list", "holiday-meal", "december-countdown"],
        extra_existing=[], preview=["holiday-planner", "gift-tracker", "card-list", "holiday-meal", "december-countdown"]),
}


def build_pdf(path: Path, size: str, label: str, pages) -> None:
    w, h = SIZES[size]
    c = canvas.Canvas(str(path), pagesize=SIZES[size])
    c.setTitle(label)
    for pg in pages:
        pg(c, w, h, size, label)
        c.showPage()
    c.save()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--existing", default="assets/digital/2026-10-23-planner-family")
    a = ap.parse_args()
    out, existing = Path(a.out), Path(a.existing)
    pdfs: dict[str, dict[str, Path]] = {}
    for key, p in PRODUCTS.items():
        d = out / key
        (d / "images").mkdir(parents=True, exist_ok=True)
        label = f"{p['year'] if p['year'].isdigit() else YEAR} {p['title'].replace(' Printable', '')}"
        pdfs[key] = {}
        n = 0
        for size in ("letter", "a4"):
            pages = p["pages"]()
            n = len(pages)
            f = d / f"{key}-{size}.pdf"
            build_pdf(f, size, label, pages)
            pdfs[key][size] = f
        guide(d / f"{key}-how-to-print.pdf", label, f"{n} pages.")
        p["page_count"] = n
        sample = [0, min(1, n - 1), min(n // 2, n - 1)]
        images(d / "images", key, p["title"], p["tagline"], p["inside"], sample, pdfs[key]["letter"],
               [f"{n} pages in each size", "Print only what you need", "Black ink with one green accent line"],
               year_label=p["year"], week_note=p["week_note"])
        print(key, n, "pages")

    for key, b in BUNDLES.items():
        d = out / key
        (d / "images").mkdir(parents=True, exist_ok=True)
        members = []
        for m in b["members"]:
            members.append((m, pdfs[m]["letter"], pdfs[m]["a4"]))
        for m in b["extra_existing"]:
            members.append((m, existing / m / f"{YEAR}-{m}-letter.pdf", existing / m / f"{YEAR}-{m}-a4.pdf"))
        for size, idx in (("letter", 1), ("a4", 2)):
            zp = d / f"{key}-{size}.zip"
            with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
                for m in members:
                    z.write(m[idx], f"{m[0]}-{size}.pdf")
            assert zp.stat().st_size < 19 * 1024 * 1024, zp
        guide(d / f"{key}-how-to-print.pdf", f"{b['year']} {b['title'].replace(' Printable', '')}", f"{len(members)} planners in each zip.")
        prev = PdfWriter()
        for m in b["preview"]:
            prev.add_page(PdfReader(str(pdfs[m]["letter"])).pages[1 if PRODUCTS[m]["pages"] is pages_monthly else 0])
        pf = d / "preview-letter.pdf"
        with open(pf, "wb") as fh:
            prev.write(fh)
        names = [PRODUCTS[m[0]]["title"].replace(" Printable", "") if m[0] in PRODUCTS else m[0].replace("-", " ").title() for m in members]
        inside = [f"{len(members)} printable planners", "US Letter and A4 zip files", *names[:3], "...and more", "How-to-print guide"]
        images(d / "images", key, b["title"], b["tagline"], inside, [0, 1, 2], pf,
               [f"{len(members)} planners per zip", "Open the zip, print what you need", "Black ink with one green accent line"],
               year_label=b["year"], week_note=False)
        print(key, len(members), "planners")


if __name__ == "__main__":
    main()
