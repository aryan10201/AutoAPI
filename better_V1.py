import requests
import time
import string
import json
from collections import deque

BASE_URL = "http://35.200.185.69:8000/v1/autocomplete"
MAX_RESULTS_PER_QUERY = 10
REQUEST_DELAY = 0.3  # Initial delay, adjusts dynamically
RETRY_DELAY = 5  # Delay for rate limit handling
SAVE_INTERVAL = 100

seen_names = set()
visited_words = set()
count = 0

RESULTS_FILE = "optimized_v1_names.json"

# Load previous results
try:
    with open(RESULTS_FILE, "r") as f:
        seen_names = set(json.load(f))
        print(f"Loaded {len(seen_names)} names from previous run.")
except FileNotFoundError:
    pass


def search_api(prefix):
    global count, REQUEST_DELAY
    while True:
        try:
            response = requests.get(BASE_URL, params={"query": prefix})
            count += 1

            if response.status_code == 429:
                print("Rate limit exceeded. Increasing delay...")
                REQUEST_DELAY = min(REQUEST_DELAY + 0.2, 5)  # Increase delay, cap at 5 sec
                time.sleep(RETRY_DELAY)
                continue

            response.raise_for_status()
            data = response.json()
            
            # Reduce delay slightly if responses are smooth
            REQUEST_DELAY = max(REQUEST_DELAY - 0.05, 0.2)

            return data.get("results", [])
        except Exception as e:
            print(f"Error: {e}. Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)


def main_function():
    queue = deque(string.ascii_lowercase)

    while queue:
        prefix = queue.popleft()
        if prefix in visited_words:
            continue
        visited_words.add(prefix)

        results = search_api(prefix)
        time.sleep(REQUEST_DELAY)

        new_names = [name for name in results if name not in seen_names]
        seen_names.update(new_names)

        if len(results) == MAX_RESULTS_PER_QUERY:
            for c in string.ascii_lowercase:
                new_prefix = prefix + c
                if new_prefix not in visited_words:
                    queue.append(new_prefix)

        if count % SAVE_INTERVAL == 0:
            save_results()

    save_results()


def save_results():
    with open(RESULTS_FILE, "w") as f:
        json.dump(sorted(seen_names), f, indent=2)
    print(f"Saved {len(seen_names)} names after {count} requests.")


if __name__ == "__main__":
    main_function()
