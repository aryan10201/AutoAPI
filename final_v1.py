import requests
import time
import string
from collections import deque
from threading import Lock
import concurrent.futures

BASE_URL = "http://35.200.185.69:8000/v1/autocomplete?query="
HEADERS = {"User-Agent": "Mozilla/5.0"}

# Rate-limit handling
INITIAL_WAIT = 0.2
MAX_WAIT = 5

# For output/data
OUTPUT_FILE = "finalV1.txt"

# Locks and shared state
rate_lock = Lock()
visited_lock = Lock()
names_lock = Lock()
queue_lock = Lock()
requests_lock = Lock()

rate_limit_wait = INITIAL_WAIT
visited_queries = set()
found_names = set()
total_requests = 0

# We’ll use a requests.Session to (possibly) reuse connections
session = requests.Session()
session.trust_env = False


def fetch_names(query):
    """
    Fetch autocomplete results for a given query with adaptive rate limiting.
    Returns a list of names. Also increments the global total_requests counter.
    """
    global rate_limit_wait, total_requests

    while True:
        try:
            response = session.get(BASE_URL + query, headers=HEADERS)

            with requests_lock:
                total_requests += 1  # Count every request attempt

            if response.status_code == 429:
                # Rate limited
                with rate_lock:
                    rate_limit_wait = min(rate_limit_wait * 1.5, MAX_WAIT)
                print(f"[429] Rate limit. Sleeping {rate_limit_wait:.1f}s ... (query='{query}')")
                time.sleep(rate_limit_wait)
                continue

            response.raise_for_status()

            # Decrease rate wait time slightly after a successful request
            with rate_lock:
                rate_limit_wait = max(rate_limit_wait * 0.8, INITIAL_WAIT)

            data = response.json()
            return data.get("results", [])

        except requests.exceptions.RequestException as e:
            print(f"Error fetching {query}: {e}. Retrying in 2s...")
            time.sleep(2)
            # Continue the loop in case of network/connection issues


def explore_query(query, queue):
    """
    Processes a single query:
      - Fetch names
      - Add unique names to found_names
      - If exactly 10 results, expand BFS with next queries
    This function is designed to be called in a thread pool.
    """
    # Make sure we don’t process the same query twice
    with visited_lock:
        if query in visited_queries:
            return
        visited_queries.add(query)

    results = fetch_names(query)
    if not results:
        return

    # Record new names
    with names_lock:
        for name in results:
            if name not in found_names:
                found_names.add(name)

    # If exactly 10 results, we expand further
    if len(results) == 10:
        last_name = results[-1]
        if len(last_name) > len(query):
            # Character after the query prefix
            pivot_char = last_name[len(query)]
            # Generate new queries from pivot_char+1 up to z
            start_ord = ord(pivot_char) + 1
            end_ord = ord('z')
            if start_ord <= end_ord:
                for c in range(start_ord, end_ord + 1):
                    next_query = query + chr(c)
                    with visited_lock:
                        if next_query not in visited_queries:
                            with queue_lock:
                                queue.append(next_query)


def explore_names():
    """
    Main BFS routine using a thread pool to process queries concurrently.
    """
    # Start queue with "aa".."zz"
    queue = deque(a + b for a in string.ascii_lowercase for b in string.ascii_lowercase)

    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        while True:
            with queue_lock:
                if not queue:
                    # If queue is empty and we've no in-flight queries, we are done
                    break
                # Grab up to some chunk of queries to process in parallel
                # (You could grab 1, or 10, or 50 - depends on how you want to batch)
                tasks = []
                for _ in range(min(len(queue), 20)):
                    q = queue.popleft()
                    tasks.append(executor.submit(explore_query, q, queue))

            # Wait for this batch to complete before grabbing next chunk
            concurrent.futures.wait(tasks, return_when=concurrent.futures.ALL_COMPLETED)

    # Save all unique names
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        for name in sorted(found_names):
            f.write(name + "\n")

    print(f"\nTotal unique names collected: {len(found_names)}")
    print(f"Total API requests made: {total_requests}")


if __name__ == "__main__":
    explore_names()