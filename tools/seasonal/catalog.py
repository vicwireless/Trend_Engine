"""Listing copy for the 2026-11-15 seasonal release: which existing listing each product replaces,
price, title, 13 tags, description parts, and what the images and pins should show.

Titles lead with the buyer's search phrase and avoid apostrophes (Etsy returns them HTML-escaped).
No brand, show, film, character or toy names (CLAUDE.md rule 3; see data/ip/2026-11-15-seasonal-ip-screen.yaml).
"""
DISCLOSURE = "Designed by the seller with AI-assisted tools (code-generated layout); see shop policies."
NICHE = "seasonal-party-games"

# key: listing_id (the planner listing it replaces), price, title, tags, hero (image headline), sub, intro,
#      gets (WHAT YOU GET bullets), show (1-based page numbers: 3 for the hero fan, 2 for the close-up), board
CATALOG = {
    "christmas-trivia": dict(
        listing_id=4601781885, price=4.99, palette="christmas", board="Christmas Party Games",
        title="Christmas Trivia Game Printable, 40 Questions with Answers, Holiday Party Game, Family or Office",
        tags=["christmas trivia", "christmas party game", "holiday trivia game", "printable xmas game", "office party game",
              "family xmas game", "christmas quiz", "trivia with answers", "holiday party games", "christmas games pdf",
              "adult christmas game", "classroom christmas", "instant download"],
        hero="Christmas Trivia", sub="40 questions + answer key",
        intro="Forty Christmas trivia questions about traditions, food and holiday history around the world. Easy enough for the family table, tricky enough for the office party.",
        gets=["4 question sheets (40 questions, 10 per sheet)", "Answer key", "The same 40 questions as cut-apart cards", "11 pages in each size"],
        show=[1, 2, 7], close=[2, 6]),
    "christmas-bingo": dict(
        listing_id=4601782191, price=4.99, palette="christmas", board="Christmas Party Games",
        title="Christmas Bingo Printable, 30 Picture Cards, Kids Classroom Party Game, Family Holiday Bingo",
        tags=["christmas bingo", "bingo cards print", "kids christmas game", "classroom party game", "holiday bingo",
              "christmas party game", "picture bingo", "preschool christmas", "family game night", "30 bingo cards",
              "school holiday party", "xmas bingo printable", "instant download"],
        hero="Christmas Bingo", sub="30 different picture cards",
        intro="Thirty different picture bingo cards with bright, hand-drawn-style holiday icons. No reading needed, so it works for preschoolers, classrooms and grandparents alike.",
        gets=["30 unique bingo cards (2 per page)", "32 picture calling cards", "How-to-play page", "18 pages in each size"],
        show=[1, 2, 17], close=[2, 3]),
    "white-elephant-kit": dict(
        listing_id=4601807284, price=4.99, palette="christmas", board="Christmas Party Games",
        title="White Elephant Gift Exchange Game Printable, Rules Sign, Numbers 1-40, Twist Cards, Party Kit",
        tags=["white elephant game", "gift exchange game", "white elephant rules", "gift swap printable", "office party game",
              "christmas party game", "gift swap numbers", "holiday party kit", "dirty santa game", "gift steal game",
              "work christmas party", "adult party game", "instant download"],
        hero="White Elephant Kit", sub="Rules sign, numbers 1-40, twist cards",
        intro="Everything you need to run a white elephant gift swap without arguing about the rules: a clear rules sign, draw numbers, optional twist cards and a steal tracker.",
        gets=["House rules sign", "Number slips 1 to 40", "12 twist cards plus 4 blanks", "Invitation notes with price limit", "Steal tracker", "8 pages in each size"],
        show=[1, 2, 5], close=[2, 3]),
    "secret-santa-kit": dict(
        listing_id=4601807452, price=4.99, palette="christmas", board="Christmas Party Games",
        title="Secret Santa Questionnaire Printable Kit, Wish List Form, Name Draw Slips, Gift Tags, Office Party",
        tags=["secret santa", "secret santa form", "santa questionnaire", "gift exchange form", "office secret santa",
              "wish list printable", "secret santa tags", "name draw slips", "coworker gift swap", "christmas party kit",
              "teacher secret santa", "holiday gift swap", "instant download"],
        hero="Secret Santa Kit", sub="Sign-up, wish list, slips, tags",
        intro="Run your office, classroom or family Secret Santa from sign-up to the big reveal. The wish-list questionnaire means nobody has to guess what to buy.",
        gets=["Sign-up sheet with price limit and date", "Wish-list questionnaire (14 prompts)", "Name draw slips", "8 gift tags", "Guess-the-giver reveal sheet", "How-it-works sign", "7 pages in each size"],
        show=[1, 3, 5], close=[3, 2]),
    "letter-to-santa-kit": dict(
        listing_id=4601807590, price=4.99, palette="christmas", board="Christmas for Kids",
        title="Letter to Santa Printable Kit, Fill In Letter, Reply from Santa, Nice List Certificate, Envelope",
        tags=["letter to santa", "santa letter kit", "letter from santa", "nice list award", "kids santa letter",
              "dear santa printable", "santa reply letter", "christmas wish list", "santa envelope", "christmas eve box",
              "kids christmas craft", "north pole mail", "instant download"],
        hero="Letter to Santa Kit", sub="Letter, reply, Nice List certificate",
        intro="A sweet Christmas tradition in one download: your child writes to Santa, and you leave a reply letter and a Nice List certificate for them to find.",
        gets=["Fill-in letter to Santa", "Blank lined letter", "Christmas wish list", "Envelope panel to cut and fold", "Reply letter from Santa with space for a name and a P.S.", "Nice List certificate", "7 pages in each size"],
        show=[1, 2, 7], close=[6, 7]),
    "christmas-left-right-game": dict(
        listing_id=4601807662, price=3.99, palette="christmas", board="Christmas Party Games",
        title="Left Right Christmas Game Printable, Gift Exchange Story, Pass the Present Party Game, Family",
        tags=["left right game", "christmas left right", "gift exchange game", "pass the gift game", "left right story",
              "christmas party game", "family xmas game", "office party game", "gift passing game", "holiday party games",
              "printable xmas game", "kids christmas game", "instant download"],
        hero="Left Right Game", sub="Pass-the-present story game",
        intro="Sit in a circle, hold a gift and listen. Every LEFT and RIGHT in this original story sends the presents around the room, and nobody knows where they will land.",
        gets=["Original family story on 2 pages (about 40 passes)", "Short story for little kids", "How-to-play sign", "5 pages in each size"],
        show=[1, 2, 4], close=[2, 3]),
    "christmas-charades": dict(
        listing_id=4601807752, price=3.99, palette="christmas", board="Christmas Party Games",
        title="Christmas Charades Game Printable, 72 Cards, Family Holiday Party Game, Kids and Adults",
        tags=["christmas charades", "charades cards", "christmas party game", "family game night", "holiday charades",
              "kids christmas game", "printable xmas game", "act it out game", "christmas eve games", "classroom party game",
              "holiday party games", "youth group game", "instant download"],
        hero="Christmas Charades", sub="72 cards, 3 levels",
        intro="Seventy-two holiday things to act out, sorted into easy, medium and tricky so kids and grown-ups can play in the same game.",
        gets=["72 charades cards (8 per page)", "3 levels: easy, medium, tricky", "Score sheet for two teams", "11 pages in each size"],
        show=[1, 2, 6], close=[2, 8]),
    "thanksgiving-trivia": dict(
        listing_id=4601807886, price=3.99, palette="thanksgiving", board="Thanksgiving Party Games",
        title="Thanksgiving Trivia Game Printable, 30 Questions with Answers, Dinner Party Game, Family",
        tags=["thanksgiving trivia", "thanksgiving game", "friends dinner game", "thanksgiving quiz", "turkey day game",
              "family dinner game", "printable trivia", "thanksgiving party", "trivia with answers", "fall party game",
              "office thanksgiving", "classroom game", "instant download"],
        hero="Thanksgiving Trivia", sub="30 questions + answer key",
        intro="Thirty Thanksgiving trivia questions on history, turkeys and the food on the table. Print it Thursday morning and play between dinner and pie, with family or friends.",
        gets=["3 question sheets (30 questions, 10 per sheet)", "Answer key", "The same 30 questions as cut-apart cards", "9 pages in each size"],
        show=[1, 2, 6], close=[2, 5]),
    "christmas-gift-certificates": dict(
        listing_id=4601035546, price=4.99, palette="christmas", board="Christmas Gift Ideas",
        title="Christmas Gift Certificate Printable, Fill In Gift Voucher, Last Minute Gift, Coupon Book",
        tags=["gift certificate", "christmas voucher", "printable gift card", "last minute gift", "coupon book print",
              "experience gift", "blank gift voucher", "christmas coupon", "gift certificate diy", "stocking stuffer",
              "gift for him", "gift for her", "instant download"],
        hero="Gift Certificates", sub="18 certificates + coupon book",
        intro="The last-minute gift that doesn't look last minute. Fill in a dinner out, a weekend away, lessons or a favor, cut it out and tuck it in a card.",
        gets=["18 fill-in gift certificates in 6 styles (3 per page)", "12 ready-made 'good for' coupons", "12 blank coupons", "9 pages in each size"],
        show=[1, 2, 8], close=[2, 4]),
    "thanksgiving-who-at-this-table": dict(
        listing_id=4601751471, price=3.99, palette="thanksgiving", board="Thanksgiving Party Games",
        title="Thanksgiving Party Game Printable, Who at This Table Cards, Dinner Icebreaker for Adults, 48 Cards",
        tags=["thanksgiving game", "thanksgiving party", "adult party game", "thanksgiving cards", "icebreaker game",
              "dinner party game", "friends dinner game", "fall party game", "printable card game", "table game adults",
              "holiday icebreaker", "turkey day game", "instant download"],
        hero="Who at This Table?", sub="Thanksgiving dinner game, 48 cards",
        intro="Who at this table would bring a store-bought pie and say it's homemade? Forty-eight friendly, family-safe prompts that get everyone pointing and laughing, whether the table is family or friends.",
        gets=["48 prompt cards (8 per page)", "8 blank cards for your own inside jokes", "Score sheet", "9 pages in each size"],
        show=[1, 2, 3], close=[2, 4]),
    "thanksgiving-kids-table": dict(
        listing_id=4601756001, price=4.99, palette="thanksgiving", board="Thanksgiving Party Games",
        title="Thanksgiving Kids Table Activities Printable, Word Search, Placemat, Pick One Cards, Games",
        tags=["thanksgiving kids", "kids table activity", "kids placemat", "word search kids", "kids thanksgiving",
              "kids table games", "thanksgiving games", "activity sheets", "thankful activity", "classroom activity",
              "fall kids printable", "turkey day kids", "instant download"],
        hero="Kids Table Activities", sub="Thanksgiving puzzles, placemat, games",
        intro="Keep the kids' table busy while the turkey rests: a word search, a scramble, drawing prompts, a placemat and silly Pick One cards.",
        gets=["Word search (18 words)", "Word scramble with answer key", "Thankful A to Z", "Draw-it page", "Placemat with tic-tac-toe", "10 Pick One cards plus blanks", "9 pages in each size"],
        show=[1, 2, 6], close=[2, 5]),
    "new-years-eve-games": dict(
        listing_id=4601781508, price=4.99, palette="nye", board="New Year's Eve Party",
        title="New Years Eve Games Printable, NYE Party Game Pack, Trivia, This or That, Family",
        tags=["new years eve games", "nye party games", "new years trivia", "new year party game", "nye printable",
              "family new years", "resolution game", "this or that game", "year in review", "new years eve party",
              "nye activities", "time capsule", "instant download"],
        hero="New Year's Eve Games", sub="5 games until midnight",
        intro="Five easy games to fill the hours before midnight: trivia, a whose-resolution guessing game, year-in-review cards, This or That and a predictions time capsule to open next year.",
        gets=["New Year trivia (20 questions) with answer key", "Whose Resolution? slips", "16 year-in-review conversation cards", "This or That sheet", "Predictions time capsule page", "9 pages in each size"],
        show=[1, 2, 6], close=[5, 8]),
    "thanksgiving-games-bundle": dict(
        listing_id=4601781681, price=11.99, palette="thanksgiving", board="Thanksgiving Party Games", bundle=True,
        title="Thanksgiving Games Bundle Printable, Dinner Party Games, Trivia, Kids Activities, 5 Games",
        tags=["thanksgiving games", "friends dinner games", "thanksgiving bundle", "party game bundle", "thanksgiving trivia",
              "kids table activity", "adult party game", "family dinner games", "this or that game", "conversation cards",
              "turkey day games", "fall party games", "instant download"],
        hero="Thanksgiving Games Bundle", sub="5 games for the whole table",
        intro="Five Thanksgiving games in one download, with something for the grown-ups, something for the kids' table and two bonus games you can only get in the bundle.",
        gets=["Thanksgiving Trivia: 30 questions, answer key and cards", "Who at This Table? dinner party game: 48 cards", "Thanksgiving Kids Table activity pack",
              "Bundle bonus: This or That (20 pairs)", "Bundle bonus: 24 conversation cards", "32 pages in each size"],
        show=[1, 3, 12], close=[29, 30]),
    "christmas-games-bundle": dict(
        listing_id=4601808366, price=14.99, palette="christmas", board="Christmas Party Games", bundle=True,
        title="Christmas Party Games Bundle Printable, 7 Family Games, Trivia, Bingo, Charades, Left Right Game",
        tags=["christmas games", "xmas game bundle", "christmas party game", "family xmas game", "christmas bingo",
              "christmas trivia", "christmas charades", "left right game", "white elephant game", "family game night",
              "scavenger hunt clues", "office party games", "instant download"],
        hero="Christmas Games Bundle", sub="7 games for family, friends, office",
        intro="Seven Christmas party games in one download: enough for the class party, the office lunch, Christmas Eve and the long afternoon after dinner. Two bonus games are only in the bundle.",
        gets=["Christmas Trivia: 40 questions, answer key and cards", "The Left Right gift-passing story game", "Christmas Bingo: 30 picture cards", "Christmas Charades: 72 cards",
              "White Elephant gift exchange kit", "Bundle bonus: Which Would You Choose? 32 cards", "Bundle bonus: indoor scavenger hunt with 12 rhyming clues", "61 pages in each size"],
        show=[1, 3, 18], close=[55, 14]),
}


def description(key: str) -> str:
    c = CATALOG[key]
    gets = "\n".join(f"• {g}" for g in c["gets"])
    return (f"{c['intro']}\n\n"
            f"WHAT YOU GET\n{gets}\n• 2 PDF files: US Letter (8.5 x 11 in) and A4\n\n"
            "HOW IT WORKS\n"
            "1. Buy and download the PDFs from your Etsy account (Purchases and reviews), or from the email Etsy sends you.\n"
            "2. Print at home, at the library or at a copy shop. Regular paper works; cardstock is nicer for cards.\n"
            "3. Cut where there are dashed lines and play. Print as many copies as your own party needs.\n\n"
            "PLEASE NOTE\n"
            "This is a digital download. Nothing will be shipped. Colors may vary slightly by printer. "
            "For personal, classroom and single-office use; please don't resell or share the files. "
            f"{DISCLOSURE}")
