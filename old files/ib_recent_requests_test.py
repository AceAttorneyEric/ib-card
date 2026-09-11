import requests

USER_ID = 72143

URL = (
    "https://infinitebacklog.net/api/user_collections"
    f"?user_id={USER_ID}"
    "&sort_field=updated_at"
    "&sort_order=desc"
    "&limit=6"
    "&offset=0"
)

print("Getting recent games from Infinite Backlog...")

response = requests.get(URL, timeout=30)
response.raise_for_status()

games = response.json()

print()
print("SUCCESS")
print()

for number, entry in enumerate(games, start=1):
    game = entry["game"]

    name = game["name"]

    cover = game.get("cover")
    cover_id = cover["url"] if cover else None

    if cover_id:
        cover_url = (
            "https://images.igdb.com/igdb/image/upload/"
            f"t_cover_big/{cover_id}"
        )
    else:
        cover_url = "NO COVER"

    print(f"{number}. {name}")
    print(f"   Cover: {cover_id}")
    print(f"   URL:   {cover_url}")
    print()

input("Press Enter to close...")