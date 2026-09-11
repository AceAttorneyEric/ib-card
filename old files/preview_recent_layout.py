from pathlib import Path
from PIL import Image, ImageOps

BASE_DIR = Path(__file__).resolve().parent

TEMPLATE_PATH = BASE_DIR / "template" / "ib_template.png"
RECENT_DIR = BASE_DIR / "recent_games"
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_PATH = OUTPUT_DIR / "recent_layout_test.png"

RECENT_GAME_COUNT = 10
SLOT_WIDTH = 38
SLOT_HEIGHT = 50
GAP = 8

# Move the whole row up/down here if needed.
ROW_Y = 97


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    base = Image.open(TEMPLATE_PATH).convert("RGBA")
    template_width, template_height = base.size

    total_row_width = (RECENT_GAME_COUNT * SLOT_WIDTH) + ((RECENT_GAME_COUNT - 1) * GAP)
    row_x = (template_width - total_row_width) // 2

    print("Template size:", template_width, "x", template_height)
    print("Row width:", total_row_width)
    print("Row starts at x =", row_x)
    print("Row y =", ROW_Y)

    for i in range(1, RECENT_GAME_COUNT + 1):
        img_path = RECENT_DIR / f"{i:02d}.jpg"
        x = row_x + (i - 1) * (SLOT_WIDTH + GAP)

        if not img_path.exists():
            print(f"Missing: {img_path.name}")
            continue

        img = Image.open(img_path).convert("RGB")

        fitted = ImageOps.fit(
            img,
            (SLOT_WIDTH, SLOT_HEIGHT),
            method=Image.Resampling.LANCZOS,
            centering=(0.5, 0.5),
        ).convert("RGBA")

        base.alpha_composite(fitted, (x, ROW_Y))

    base.save(OUTPUT_PATH)
    print()
    print("Done.")
    print("Saved to:", OUTPUT_PATH)


if __name__ == "__main__":
    main()