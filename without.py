import requests
import time
import json
import string
from typing import Literal
from urllib.parse import quote


class SuggestionExtractor:
    def __init__(self, api_url: str, max_items: int, characters: str, api_version: Literal["v1", "v2", "v3"]):
        self.api_url = api_url
        self.max_items = max_items
        self.unique_suggestions = set()
        self.api_requests = 0
        self.characters = sorted(characters)
        self.api_version = api_version

    def fetch_suggestions(self, search_query: str):
        encoded_query = quote(search_query)
        request_url = f"{self.api_url}/{self.api_version}/autocomplete?query={encoded_query}&max_results={self.max_items}"

        try:
            response = requests.get(request_url)
            self.api_requests += 1

            if response.status_code == 429:
                time.sleep(10)
                return self.fetch_suggestions(search_query)

            if response.status_code != 200:
                return []

            response_data = response.json()

            if "results" in response_data and isinstance(response_data["results"], list):
                suggestions = response_data["results"]

                if suggestions:
                    return suggestions
                else:
                    return []
            else:
                return []

        except Exception as error:
            return []

    def extract_suggestions(self):
        start_time = time.time()

        for initial_character in self.characters:
            if initial_character == " ":
                continue  # Skip spaces
            self.process_prefix(initial_character)

        elapsed_time = time.time() - start_time
        return self.unique_suggestions, elapsed_time, self.api_requests

    def process_prefix(self, prefix: str):
        suggestions = self.fetch_suggestions(prefix)

        for suggestion in suggestions:
            self.unique_suggestions.add(suggestion)

        if len(suggestions) == self.max_items:
            next_character = suggestions[-1][len(prefix)]
            index = self.characters.index(next_character)
            for next_character in self.characters[index:]:
                if next_character == " ":
                    continue
                new_prefix = prefix + next_character
                self.process_prefix(new_prefix)

    def store_results(self, output_file="unique_suggestions.json"):
        results = {
            "total_requests": self.api_requests,
            "total_suggestions": len(self.unique_suggestions),
            "suggestions": sorted(list(self.unique_suggestions)),
        }

        with open(output_file, "w") as file:
            json.dump(results, file, indent=2)

        print(f"Results saved to {output_file}")


def main():
    extractor = SuggestionExtractor(
        "http://35.207.196.198:8000", 50, string.ascii_lowercase, "v1"
    )

    suggestions, duration, request_count = extractor.extract_suggestions()
    extractor.store_results()

    print(f"Extraction complete. Found {len(suggestions)} unique suggestions.")
    print(f"Made {request_count} API requests in {duration:.2f} seconds.")


if __name__ == "__main__":
    main()