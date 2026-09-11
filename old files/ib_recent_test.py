from playwright.sync_api import sync_playwright
import json

URL = "https://infinitebacklog.net/users/aceattorneyeric/collection?sort=updated_at&order=desc"

interesting_responses = []

print("Opening Infinite Backlog collection...")

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()

    def handle_response(response):
        url = response.url.lower()

        if any(word in url for word in [
            "collection",
            "game",
            "user",
            "library"
        ]):
            try:
                content_type = response.headers.get("content-type", "")

                if "application/json" in content_type:
                    data = response.json()

                    interesting_responses.append({
                        "url": response.url,
                        "data": data
                    })

                    print()
                    print("JSON:")
                    print(response.url)

            except Exception:
                pass

    page.on("response", handle_response)

    page.goto(URL, wait_until="networkidle", timeout=60000)
    page.wait_for_timeout(3000)

    browser.close()

with open(
    "ib_recent_network.json",
    "w",
    encoding="utf-8"
) as f:
    json.dump(
        interesting_responses,
        f,
        indent=2,
        ensure_ascii=False
    )

print()
print("DONE")
print(f"Captured {len(interesting_responses)} JSON responses.")
print("Saved as ib_recent_network.json")
print()
input("Press Enter to close...")