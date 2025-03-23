import requests
import time
import string
import json
from collections import deque

BASE_URL = "http://35.200.185.69:8000/v3/autocomplete"
# HEADERS = {"User-Agent": "NameExtractorBot/1.0"}

MAX_RESULTS_PER_QUERY = 15
REQUEST_DELAY = 1.2
RETRY_DELAY = 5      
SAVE_INTERVAL = 100

seenNames = set()
visitedWords = set()
count = 0

# Output file
RESULTS_FILE = "v3_names.json"

# Try to resume if possible
try:
    with open(RESULTS_FILE, "r") as f:
        seenNames = set(json.load(f))
        print(f"Loaded {len(seenNames)} names from previous run.")
except FileNotFoundError:
    pass

CHARSET = string.ascii_lowercase + string.digits + "+-. "

def search_api(prefix):
    global count
    while True:
        try:
            response = requests.get(BASE_URL, params={"query": prefix})
            count += 1

            if response.status_code == 429:
                print("Rate limit exceeded. Sleeping before retrying...")
                time.sleep(RETRY_DELAY)
                continue

            response.raise_for_status()
            data = response.json()
            return data.get("results", [])
        except Exception as e:
            print(f"Error: {e}. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)


def mainFunction():
    queue = deque(CHARSET)

    while queue:
        prefix = queue.popleft()
        if prefix in visitedWords:
            continue
        visitedWords.add(prefix)

        results = search_api(prefix)
        time.sleep(REQUEST_DELAY)

        newNames = [name for name in results if name not in seenNames]
        seenNames.update(newNames)

        if len(results) == MAX_RESULTS_PER_QUERY:
            for c in CHARSET:
                new_prefix = prefix + c
                if new_prefix not in visitedWords:
                    queue.append(new_prefix)

        # Save periodically
        if count % SAVE_INTERVAL == 0:
            save_results()

    # Final save
    save_results()


def save_results():
    with open(RESULTS_FILE, "w") as f:
        json.dump(sorted(seenNames), f, indent=2)
    print(f"Saved {len(seenNames)} names after {count} requests.")


if __name__ == "__main__":
    mainFunction()