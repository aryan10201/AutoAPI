import requests
import time
import json
import string
import threading
from typing import Literal
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor, as_completed

class AutocompleteExtractor:
    def __init__(self, base_url: str, max_results: int, charlist: str, version: Literal["v1", "v2", "v3"]):
        self.base_url = base_url
        self.max_results = max_results
        self.discovered_names = set()
        self.request_count = 0
        self.charlist = sorted(charlist)
        self.version = version

        # Lock to protect shared variables (discovered_names and request_count) in concurrent code
        self.lock = threading.Lock()

    def get_autocomplete_suggestions(self, query: str):
        query_encoded = quote(query)
        url = f"{self.base_url}/{self.version}/autocomplete?query={query_encoded}&max_results={self.max_results}"

        try:
            response = requests.get(url)
            with self.lock:
                self.request_count += 1

            # Handle rate limiting (status 429)
            if response.status_code == 429:
                print(f"Rate limited. Sleeping for 30 seconds (query='{query}').")
                time.sleep(30)
                return self.get_autocomplete_suggestions(query)

            if response.status_code != 200:
                print(f"Error status code: {response.status_code} (query='{query}'). Sleeping for 1s...")
                time.sleep(1)
                return []

            data = response.json()
            if "results" in data and isinstance(data["results"], list):
                suggestions: list = data["results"]
                return suggestions
            else:
                print(f"Unexpected response format for '{query}': {data.keys()}")
                return []

        except Exception as e:
            print(f"Error querying '{query}': {str(e)}")
            return []

    def crawl_autocomplete(self):
        print(f"Starting extraction with max_results={self.max_results}")
        start_time = time.time()

        # We'll process the single-letter prefixes concurrently using a ThreadPoolExecutor
        futures = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for first_letter in self.charlist:
                if first_letter == " ":
                    continue  # Skip space
                futures.append(executor.submit(self.crawl_prefix, first_letter))

            # Ensure all tasks complete
            for future in as_completed(futures):
                _ = future.result()  # We ignore the result; data is stored in shared sets

        elapsed_time = time.time() - start_time
        print(f"Extraction completed in {elapsed_time:.2f} seconds")
        print(f"Total API requests: {self.request_count}")
        print(f"Total names discovered: {len(self.discovered_names)}")

        return self.discovered_names

    def crawl_prefix(self, prefix: str):
        suggestions = self.get_autocomplete_suggestions(prefix)

        # Add all suggestions to our discovered names (thread-safe)
        with self.lock:
            for name in suggestions:
                self.discovered_names.add(name)

        # If we got exactly max_results, explore further by trying next characters
        if len(suggestions) == self.max_results and suggestions:
            # We assume that if suggestions are exactly max_results, the last name
            # might indicate there's more deeper matches
            last_name = suggestions[-1]
            if len(last_name) > len(prefix):
                # Grab the character in the last result that goes beyond the prefix
                next_char = last_name[len(prefix)]
                if next_char in self.charlist:
                    ind = self.charlist.index(next_char)
                    for char in self.charlist[ind:]:
                        if char == " ":
                            continue
                        next_prefix = prefix + char
                        self.crawl_prefix(next_prefix)

    def save_results(self, output_file="v3_names.json"):
        results = {
            "total_requests": self.request_count,
            "total_names": len(self.discovered_names),
            "names": sorted(list(self.discovered_names)),
        }

        with open(output_file, "w") as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to {output_file}")

def main():
    extractor = AutocompleteExtractor(
        base_url="http://35.207.196.198:8000",
        max_results=100,
        charlist=string.ascii_lowercase + string.digits  + "+-." + " ",
        version="v3"
    )

    all_names = extractor.crawl_autocomplete()
    extractor.save_results()

    print(f"Extraction complete. Found {len(all_names)} names.")
    print(f"Made {extractor.request_count} API requests.")

if __name__ == "__main__":
    main()
