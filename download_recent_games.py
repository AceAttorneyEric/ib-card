import json
from pathlib import Path

import requests


USER_ID = 72143
RECENT_GAME_COUNT = 10

BASE_DIR = Path(__file__).resolve().parent
RECENT_DIR = BASE_DIR / "recent_games"
MANIFEST_FILE = RECENT_DIR / "recent_games.json"

COLLECTION_URL = (
    "https://infinitebacklog.net/api/user_collections"
    f"?user_id={USER_ID}"
    "&sort_field=updated_at"
    "&sort_order=desc"
    f"&limit={RECENT_GAME_COUNT}"
    "&offset=0"
)

IGDB_BASE_URL = (
    "https://images.igdb.com/igdb/image/upload/t_cover_big/"
)


def get_json(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def download_image(url, destination):
    response = requests.get(url, timeout=30)
    response.raise_for_status()

    destination.write_bytes(response.content)


print("Getting recent games from Infinite Backlog...")

RECENT_DIR.mkdir(exist_ok=True)

# Remove only previously downloaded numbered cover files.
for old_file in RECENT_DIR.glob("*.jpg"):
    if old_file.stem.isdigit():
        old_file.unlink()

games = get_json(COLLECTION_URL)

manifest = []

print()

for number, entry in enumerate(games, start=1):
    game = entry["game"]

    name = game["name"]
    cover = game.get("cover")

    if not cover or not cover.get("url"):
        print(f"{number}. {name}")
        print("   No cover available. Skipping.")
        print()
        continue

    cover_id = cover["url"]
    cover_url = IGDB_BASE_URL + cover_id

    destination = RECENT_DIR / f"{number:02d}.jpg"

    print(f"{number}. {name}")
    print(f"   Downloading {cover_id}...")

    download_image(cover_url, destination)

    manifest.append({
        "position": number,
        "name": name,
        "game_id": game["id"],
        "cover_id": cover_id,
        "cover_url": cover_url,
        "file": destination.name,
        "updated_at": entry.get("updated_at")
    })

with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print()
print("SUCCESS")
print(f"Downloaded {len(manifest)} covers.")
print(f"Saved to: {RECENT_DIR}")
print()