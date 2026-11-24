"""Listing copy for the 2026-11-15 seasonal release: which existing listing each product replaces,
price, title, 13 tags, description parts, and what the images and pins should show.

Titles lead with the buyer's search phrase and avoid apostrophes (Etsy returns them HTML-escaped).
No brand, show, film, character or toy names (CLAUDE.md rule 3; see data/ip/2026-11-15-seasonal-ip-screen.yaml).
"""
DISCLOSURE = "Designed by the seller with AI-assisted tools (code-generated layout); see shop policies."
NICHE = "seasonal-party-games"
ADDONS_2026_11_24 = ["christmas-word-games", "christmas-gift-tags", "christmas-table-games", "new-years-eve-kids-pack"]

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
    # ---- 2026-11-24 add-ons. They take the four listings the dropped Thanksgiving products would have used.
    "christmas-word-games": dict(
        listing_id=4601807886, price=3.99, palette="christmas", board="Christmas for Kids",
        title="Christmas Word Search Printable, Kids Word Games, Word Scramble, Classroom Party Activity Sheets",
        tags=["xmas word search", "kids christmas game", "word scramble", "classroom activity", "christmas puzzles",
              "kids activity sheets", "christmas worksheet", "holiday word search", "school party game", "road trip activity",
              "christmas printable", "puzzles with answers", "instant download"],
        hero="Christmas Word Games", sub="2 word searches, scramble, answers",
        intro="Quiet holiday fun for the class party, the kids' table or a long car ride: an easy word search, a big one, a word scramble and an A to Z challenge, with answer keys.",
        gets=["Easy word search (12 words)", "Big word search (18 words)", "Word scramble (12 words)", "Christmas A to Z page", "Answer keys for all three puzzles", "8 pages in each size"],
        show=[1, 2, 3], close=[3, 7]),
    "christmas-gift-tags": dict(
        listing_id=4601751471, price=3.99, palette="christmas", board="Christmas Gift Ideas",
        title="Christmas Gift Tags Printable, To From Labels, Holiday Present Tags, 60 Tags to Print",
        tags=["christmas gift tags", "printable gift tags", "to from tags", "holiday gift labels", "present tags",
              "gift wrap printable", "christmas labels", "diy gift tags", "sticker paper tags", "last minute wrap",
              "christmas printable", "gift tag sheet", "instant download"],
        hero="Christmas Gift Tags", sub="60 tags, print and cut",
        intro="Out of gift tags on wrapping night? Print these at home on cardstock or sticker paper: 60 To/From tags in 24 hand-drawn-style holiday designs, plus blanks for your own message.",
        gets=["48 small tags in 24 designs", "12 large tags for big boxes and gift bags", "8 blank write-your-own tags", "8 pages in each size"],
        show=[1, 2, 6], close=[2, 6]),
    "christmas-table-games": dict(
        listing_id=4601756001, price=3.99, palette="christmas", board="Christmas Party Games",
        title="Christmas Dinner Games Printable, This or That, Conversation Cards, Family Awards, Table Games",
        tags=["xmas dinner game", "xmas table game", "this or that game", "conversation cards", "family christmas",
              "holiday dinner party", "christmas icebreaker", "family awards", "place setting game", "christmas eve games",
              "adult christmas game", "christmas party game", "instant download"],
        hero="Christmas Table Games", sub="3 games for the dinner table",
        intro="Three easy games that work while everyone is still sitting down: a This or That sheet for every place setting, conversation cards for the middle of the table, and a secret-ballot family awards vote for after dessert.",
        gets=["This or That, Christmas edition (20 pairs)", "24 conversation cards", "Family awards ballot (12 awards)", "Awards tally sheet", "7 pages in each size"],
        show=[1, 2, 3], close=[2, 6]),
    "new-years-eve-kids-pack": dict(
        listing_id=4601781681, price=4.99, palette="nye", board="New Year's Eve Party",
        title="New Years Eve Kids Activities Printable, Countdown Bags Tags, Year in Review, NYE Party Games",
        tags=["new years eve kids", "nye countdown bags", "kids new year party", "countdown bag tags", "year in review kids",
              "nye kids activities", "new years printable", "noon year eve", "family new years", "kids time capsule",
              "nye word search", "nye party kids", "instant download"],
        hero="New Year's Eve for Kids", sub="Countdown bags + activities",
        intro="Turn New Year's Eve into a countdown party for kids: tape a tag to each bag, open one every hour, and finish with noise makers. Works for a real midnight or an early countdown at noon or 8 pm.",
        gets=["8 countdown bag tags with ready-made activities", "8 blank tags for your own ideas", "My Year in Review page", "My Wishes for Next Year page",
              "Pick One game (10 pairs)", "Word search (16 words) with answer key", "8 pages in each size"],
        show=[1, 2, 4], close=[2, 5]),
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
