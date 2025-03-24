import requests
import time
import string
import json
from collections import deque

API_ENDPOINT = "http://35.200.185.69:8000/v2/autocomplete"

MAX_RESULTS_PER_QUERY = 12
REQUEST_DELAY_SECONDS = 1.2
RETRY_DELAY_SECONDS = 5
SAVE_INTERVAL_REQUESTS = 100


extracted_names = set()
processed_prefixes = set()
api_request_count = 0
extracted_names_count = 0

OUTPUT_FILENAME = "v2_names.json"

# Attempt to load previously extracted names from file
try:
    with open(OUTPUT_FILENAME, "r") as file:
        loaded_data = json.load(file)
        extracted_names = set(loaded_data['names']) # Load names from JSON structure
        api_request_count = loaded_data.get('request_count', 0) # Load previous request count if available
        extracted_names_count = len(extracted_names)
        print(f"Loaded {extracted_names_count} names from '{OUTPUT_FILENAME}'.")
except FileNotFoundError:
    print(f"Starting fresh. '{OUTPUT_FILENAME}' not found.")
except json.JSONDecodeError:
    print(f"Warning: JSON decoding error encountered while loading '{OUTPUT_FILENAME}'. Starting with empty name set.")
    extracted_names = set()# Character set to expand prefixes (lowercase letters and digits)
CHARACTER_SET = string.ascii_lowercase + string.digits

def fetch_data_from_api(prefix):
    """
    Fetches autocomplete suggestions from the API for a given prefix.
    Handles rate limiting and other potential request errors with retries.

    """
    global api_request_count
    while True:
        try:
            response = requests.get(API_ENDPOINT, params={"query": prefix})
            api_request_count += 1

            if response.status_code == 429:
                print(f"API Rate limit hit for prefix '{prefix}'. Waiting {RETRY_DELAY_SECONDS} seconds before retry...")
                time.sleep(RETRY_DELAY_SECONDS)
                continue # Retry the request
            response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)
            data = response.json()
            return data.get("results", []) # Return list of results, empty list if 'results' key is not present
        except requests.exceptions.RequestException as e:
            print(f"Request error for prefix '{prefix}': {e}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
            time.sleep(RETRY_DELAY_SECONDS)
        except json.JSONDecodeError as e:
            print(f"JSON decode error for prefix '{prefix}': {e}. Retrying in {RETRY_DELAY_SECONDS} seconds...")
            time.sleep(RETRY_DELAY_SECONDS)


def main_execution():
    """
    Main function to orchestrate the process of querying the API,
    extracting names, and managing the search space using a queue.
    """
    prefix_queue = deque(CHARACTER_SET) # Initialize queue with single characters

    while prefix_queue:
        current_prefix = prefix_queue.popleft()
        if current_prefix in processed_prefixes:
            continue # Skip prefixes already processed
        processed_prefixes.add(current_prefix)

        results = fetch_data_from_api(current_prefix) # Fetch results from API
        time.sleep(REQUEST_DELAY_SECONDS) # соблюдаем delay между запросами

        new_names = [name for name in results if name not in extracted_names] # Filter out already seen names
        extracted_names.update(new_names) # Add new names to the set
        global extracted_names_count
        extracted_names_count = len(extracted_names) # Update the global count

        if len(results) == MAX_RESULTS_PER_QUERY:
            # If max results are returned, there might be more names with longer prefixes
            for char in CHARACTER_SET:
                next_prefix = current_prefix + char
                if next_prefix not in processed_prefixes:
                    prefix_queue.append(next_prefix) # Add new prefixes to queue for further exploration

        if api_request_count % SAVE_INTERVAL_REQUESTS == 0:
            persist_results() # Save results periodically

    persist_results() # Final save after queue is empty


def persist_results():
    """
    Saves the extracted names, along with request count and extracted names count,
    to a JSON file.    """
    output_data = {
        "names": sorted(list(extracted_names)),
        "request_count": api_request_count,
        "extracted_names_count": extracted_names_count
    }
    with open(OUTPUT_FILENAME, "w") as file:
        json.dump(output_data, file, indent=2)
    print(f"Saved {extracted_names_count} unique names to '{OUTPUT_FILENAME}' after {api_request_count} API requests.")


if __name__ == "__main__":
    main_execution()