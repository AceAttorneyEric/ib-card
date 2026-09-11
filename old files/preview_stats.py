from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont


USER_ID = 72143

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_PATH = BASE_DIR / "template" / "ib_template.png"
FONT_PATH = BASE_DIR / "fonts" / "Montserrat-VariableFont_wght.ttf"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_PATH = OUTPUT_DIR / "stats_layout_test.png"

GENERAL_URL = f"https://infinitebacklog.net/api/users/{USER_ID}/statistics"
COLLECTION_URL = f"https://infinitebacklog.net/api/users/{USER_ID}/statistics/collection"
DETAIL_URL = f"https://infinitebacklog.net/api/users/{USER_ID}/statistics/detail"

# Stat number placement
GAMES_X = 106
FINISHED_X = 169
BACKLOG_X = 229
ACHIEVEMENTS_X = 296

STAT_Y = 59
FONT_SIZE = 10

TEXT_COLOR = (255, 255, 255)


def get_json(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def format_number(number):
    if number >= 1000:
        value = number / 1000

        if value >= 10:
            return f"{value:.0f}K"

        return f"{value:.1f}K"

    return str(number)


def main():
    print("Getting live Infinite Backlog stats...")

    general = get_json(GENERAL_URL)
    collection = get_json(COLLECTION_URL)
    detail = get_json(DETAIL_URL)

    games = general["collection"]["collection_total"]
    finished = collection["finished"]
    backlog = collection["backlog"]
    achievements = detail["achievements"]

    print()
    print(f"Games:        {games}")
    print(f"Finished:     {finished}")
    print(f"Backlog:      {backlog}")
    print(f"Achievements: {achievements}")

    OUTPUT_DIR.mkdir(exist_ok=True)

    card = Image.open(TEMPLATE_PATH).convert("RGBA")
    draw = ImageDraw.Draw(card)

    font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)

    # Use Montserrat's actual Bold weight.
    font.set_variation_by_name("Bold")

    stats = [
        (GAMES_X, str(games)),
        (FINISHED_X, str(finished)),
        (BACKLOG_X, str(backlog)),
        (ACHIEVEMENTS_X, format_number(achievements)),
    ]

    for x, text in stats:
        draw.text(
            (x, STAT_Y),
            text,
            font=font,
            fill=TEXT_COLOR,
            anchor="mm"
        )

    card.save(OUTPUT_PATH)

    print()
    print("SUCCESS")
    print("Saved preview to:")
    print(OUTPUT_PATH)
    print()
    input("Press Enter to close...")


if __name__ == "__main__":
    main()