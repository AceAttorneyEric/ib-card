from pathlib import Path

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps


USER_ID = 72143

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_PATH = BASE_DIR / "template" / "ib_template.png"
FONT_PATH = BASE_DIR / "fonts" / "Montserrat-VariableFont_wght.ttf"
RECENT_DIR = BASE_DIR / "recent_games"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_PATH = OUTPUT_DIR / "full_card_preview.png"

GENERAL_URL = f"https://infinitebacklog.net/api/users/{USER_ID}/statistics"
COLLECTION_URL = f"https://infinitebacklog.net/api/users/{USER_ID}/statistics/collection"
DETAIL_URL = f"https://infinitebacklog.net/api/users/{USER_ID}/statistics/detail"

# ---------------------------
# STAT NUMBER POSITIONS
# ---------------------------
GAMES_X = 106
FINISHED_X = 169
BACKLOG_X = 229
ACHIEVEMENTS_X = 296
STAT_Y = 59
FONT_SIZE = 10

# ---------------------------
# RECENT GAME ROW
# ---------------------------
RECENT_GAME_COUNT = 10
SLOT_WIDTH = 38
SLOT_HEIGHT = 50
GAP = 8
ROW_Y = 97

TEXT_COLOR = (255, 255, 255)
PLACEHOLDER_OUTLINE = (0, 200, 255, 120)
PLACEHOLDER_FILL = (10, 25, 45, 160)


def get_json(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def format_number(number):
    if number >= 1000:
        value = number / 1000

        if value >= 10:
            return f"{value:.1f}K".replace(".0K", "K")

        return f"{value:.1f}K"

    return str(number)


def get_recent_image_path(index):
    jpg_path = RECENT_DIR / f"{index:02d}.jpg"
    png_path = RECENT_DIR / f"{index:02d}.png"

    if jpg_path.exists():
        return jpg_path
    if png_path.exists():
        return png_path

    return None


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

    # Font
    font = ImageFont.truetype(str(FONT_PATH), FONT_SIZE)
    try:
        font.set_variation_by_name("Bold")
    except Exception:
        pass

    # ---------------------------
    # DRAW THE 4 STATS
    # ---------------------------
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

    # ---------------------------
    # DRAW RECENT GAME COVERS
    # ---------------------------
    template_width, template_height = card.size
    total_row_width = (RECENT_GAME_COUNT * SLOT_WIDTH) + ((RECENT_GAME_COUNT - 1) * GAP)
    row_x = (template_width - total_row_width) // 2

    print()
    print("Recent row info:")
    print(f"Template size: {template_width} x {template_height}")
    print(f"Row starts at x = {row_x}")
    print(f"Row y = {ROW_Y}")

    for i in range(1, RECENT_GAME_COUNT + 1):
        x = row_x + (i - 1) * (SLOT_WIDTH + GAP)
        y = ROW_Y

        img_path = get_recent_image_path(i)

        if img_path is None:
            # Placeholder box if missing
            draw.rounded_rectangle(
                [x, y, x + SLOT_WIDTH, y + SLOT_HEIGHT],
                radius=2,
                fill=PLACEHOLDER_FILL,
                outline=PLACEHOLDER_OUTLINE,
                width=1
            )
            print(f"Missing recent image: {i:02d}")
            continue

        img = Image.open(img_path).convert("RGB")
        fitted = ImageOps.fit(
            img,
            (SLOT_WIDTH, SLOT_HEIGHT),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        ).convert("RGBA")

        card.alpha_composite(fitted, (x, y))
        print(f"Placed: {img_path.name}")

    card.save(OUTPUT_PATH)

    print()
    print("SUCCESS")
    print("Saved preview to:")
    print(OUTPUT_PATH)
    print()
    input("Press Enter to close...")


if __name__ == "__main__":
    main()