import requests

USER_ID = 72143

GENERAL_URL = f"https://infinitebacklog.net/api/users/{USER_ID}/statistics"
COLLECTION_URL = f"https://infinitebacklog.net/api/users/{USER_ID}/statistics/collection"
DETAIL_URL = f"https://infinitebacklog.net/api/users/{USER_ID}/statistics/detail"


def get_json(url):
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


print("Connecting to Infinite Backlog...")

general = get_json(GENERAL_URL)
collection = get_json(COLLECTION_URL)
detail = get_json(DETAIL_URL)

# Convert Infinite Backlog's completion list into an easy dictionary.
completion_totals = {
    item["completion"]: item["total"]
    for item in general["user_collection"]["total_per_completion"]
}

not_started = completion_totals.get("notStarted", 0)
unfinished = completion_totals.get("unfinished", 0)
beaten = completion_totals.get("campaignCompleted", 0)
completed = completion_totals.get("completed", 0)
continuous = completion_totals.get("continuous", 0)

games = general["collection"]["collection_total"]
finished = collection["finished"]
backlog = collection["backlog"]
achievements = detail["achievements"]

print()
print("SUCCESS")
print()
print(f"Games:         {games}")
print(f"Finished:      {finished}")
print(f"Backlog:       {backlog}")
print(f"Achievements:  {achievements}")
print()
print("Donut:")
print(f"  Not Started: {not_started}")
print(f"  Unfinished:  {unfinished}")
print(f"  Beaten:      {beaten}")
print(f"  Completed:   {completed}")
print(f"  Continuous:  {continuous}")
print()
input("Press Enter to close...")