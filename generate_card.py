from pathlib import Path
import shutil

import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps


USERNAME = "aceattorneyeric"
BASE_URL = "https://infinitebacklog.net"

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_PATH = BASE_DIR / "template" / "ib_template.png"
FONT_PATH = BASE_DIR / "fonts" / "Montserrat-VariableFont_wght.ttf"
RECENT_DIR = BASE_DIR / "recent_games"
OUTPUT_DIR = BASE_DIR / "output"
DOCS_DIR = BASE_DIR / "docs"

OUTPUT_PATH = OUTPUT_DIR / "ib-card.png"
DOCS_OUTPUT_PATH = DOCS_DIR / "ib-card.png"

# ----- stat number placement -----
GAMES_X = 106
FINISHED_X = 169
BACKLOG_X = 229
ACHIEVEMENTS_X = 296
STAT_Y = 59
STAT_FONT_SIZE = 10

# ----- recent games row -----
RECENT_GAME_COUNT = 10
SLOT_WIDTH = 38
SLOT_HEIGHT = 50
GAP = 8
ROW_Y = 97

# ----- donut placement -----
PIE_CENTER_X = 380
PIE_CENTER_Y = 53
PIE_OUTER_RADIUS = 37
PIE_INNER_RADIUS = 23
PIE_NUMBER_Y = PIE_CENTER_Y - 3
PIE_NUMBER_FONT_SIZE = 16

TEXT_COLOR = (255, 255, 255, 255)

# Exact legend colors
PIE_COLORS = {
    "notStarted": (211, 62, 59, 255),
    "unfinished": (244, 190, 50, 255),
    "campaignCompleted": (83, 147, 67, 255),
    "completed": (63, 166, 237, 255),
    "continuous": (23, 72, 134, 255),
}


def get_json(session, url):
    response = session.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def get_bold_font(size):
    font = ImageFont.truetype(str(FONT_PATH), size)
    try:
        font.set_variation_by_name("Bold")
    except Exception:
        pass
    return font


def format_number(number):
    if number >= 1000:
        value = number / 1000
        if value >= 10:
            return f"{value:.1f}K"
        return f"{value:.1f}K"
    return str(number)


def resolve_user_id(session):
    user = get_json(session, f"{BASE_URL}/api/users/username/{USERNAME}")
    return user["id"]


def fetch_live_data(session, user_id):
    general = get_json(session, f"{BASE_URL}/api/users/{user_id}/statistics")
    collection = get_json(session, f"{BASE_URL}/api/users/{user_id}/statistics/collection")
    detail = get_json(session, f"{BASE_URL}/api/users/{user_id}/statistics/detail")

    completion_counts = {
        item["completion"]: item["total"]
        for item in collection.get("total_per_completion", [])
    }

    games = detail.get("played")
    if games is None:
        games = general.get("collection", {}).get("collection_total", 0)

    finished = collection.get("finished", 0)
    backlog = collection.get("backlog", 0)
    achievements = detail.get("achievements", 0)

    return {
        "games": games,
        "finished": finished,
        "backlog": backlog,
        "achievements": achievements,
        "completion_counts": completion_counts,
    }


def draw_stats(card, data):
    draw = ImageDraw.Draw(card)
    font = get_bold_font(STAT_FONT_SIZE)

    stats = [
        (GAMES_X, str(data["games"])),
        (FINISHED_X, str(data["finished"])),
        (BACKLOG_X, str(data["backlog"])),
        (ACHIEVEMENTS_X, format_number(data["achievements"])),
    ]

    for x, text in stats:
        draw.text(
            (x, STAT_Y),
            text,
            font=font,
            fill=TEXT_COLOR,
            anchor="mm"
        )


def find_recent_image(index):
    candidates = [
        RECENT_DIR / f"{index:02d}.jpg",
        RECENT_DIR / f"{index:02d}.jpeg",
        RECENT_DIR / f"{index:02d}.png",
        RECENT_DIR / f"{index:02d}.webp",
    ]

    for path in candidates:
        if path.exists():
            return path

    return None


def draw_recent_games(card):
    template_width, _ = card.size
    total_row_width = (RECENT_GAME_COUNT * SLOT_WIDTH) + ((RECENT_GAME_COUNT - 1) * GAP)
    row_x = (template_width - total_row_width) // 2

    for i in range(1, RECENT_GAME_COUNT + 1):
        img_path = find_recent_image(i)
        x = row_x + (i - 1) * (SLOT_WIDTH + GAP)

        if img_path is None:
            continue

        img = Image.open(img_path).convert("RGB")

        fitted = ImageOps.fit(
            img,
            (SLOT_WIDTH, SLOT_HEIGHT),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        ).convert("RGBA")

        card.alpha_composite(fitted, (x, ROW_Y))


def draw_donut(card, counts, total_games):
    order = [
        "notStarted",
        "unfinished",
        "campaignCompleted",
        "completed",
        "continuous",
    ]

    total = sum(counts.get(key, 0) for key in order)

    if total <= 0:
        return

    # Draw at larger size first, then shrink for smooth edges
    scale = 6

    large_layer = Image.new(
        "RGBA",
        (card.width * scale, card.height * scale),
        (0, 0, 0, 0)
    )
    large_draw = ImageDraw.Draw(large_layer)

    cx = PIE_CENTER_X * scale
    cy = PIE_CENTER_Y * scale
    outer = PIE_OUTER_RADIUS * scale
    inner = PIE_INNER_RADIUS * scale

    outer_bbox = [
        cx - outer,
        cy - outer,
        cx + outer,
        cy + outer,
    ]

    start_angle = -90

    for key in order:
        value = counts.get(key, 0)

        if value <= 0:
            continue

        sweep = (value / total) * 360
        end_angle = start_angle + sweep

        large_draw.pieslice(
            outer_bbox,
            start=start_angle,
            end=end_angle,
            fill=PIE_COLORS[key]
        )

        start_angle = end_angle

    # Transparent hole so the template center shows through
    inner_bbox = [
        cx - inner,
        cy - inner,
        cx + inner,
        cy + inner,
    ]

    large_draw.ellipse(
        inner_bbox,
        fill=(0, 0, 0, 0)
    )

    donut_layer = large_layer.resize(
        card.size,
        Image.Resampling.LANCZOS
    )

    card.alpha_composite(donut_layer)

    # Draw only the live number. "Total" stays in the template.
    draw = ImageDraw.Draw(card)
    number_font = get_bold_font(PIE_NUMBER_FONT_SIZE)

    draw.text(
        (PIE_CENTER_X, PIE_NUMBER_Y),
        str(total_games),
        font=number_font,
        fill=TEXT_COLOR,
        anchor="mm"
    )


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)
    DOCS_DIR.mkdir(exist_ok=True)

    session = requests.Session()
    session.headers.update({
        "User-Agent": "Mozilla/5.0"
    })

    print("Getting live Infinite Backlog data...")

    user_id = resolve_user_id(session)
    data = fetch_live_data(session, user_id)

    print()
    print("SUCCESS")
    print(f"Games:        {data['games']}")
    print(f"Finished:     {data['finished']}")
    print(f"Backlog:      {data['backlog']}")
    print(f"Achievements: {data['achievements']}")
    print()
    print("Completion breakdown:")
    print(f"  Not Started: {data['completion_counts'].get('notStarted', 0)}")
    print(f"  Unfinished:  {data['completion_counts'].get('unfinished', 0)}")
    print(f"  Beaten:      {data['completion_counts'].get('campaignCompleted', 0)}")
    print(f"  Completed:   {data['completion_counts'].get('completed', 0)}")
    print(f"  Continuous:  {data['completion_counts'].get('continuous', 0)}")

    card = Image.open(TEMPLATE_PATH).convert("RGBA")

    draw_stats(card, data)
    draw_recent_games(card)
    draw_donut(card, data["completion_counts"], data["games"])

    card.save(OUTPUT_PATH)
    shutil.copy2(OUTPUT_PATH, DOCS_OUTPUT_PATH)

    print()
    print("Saved card to:")
    print(OUTPUT_PATH)
    print(DOCS_OUTPUT_PATH)


if __name__ == "__main__":
    main()