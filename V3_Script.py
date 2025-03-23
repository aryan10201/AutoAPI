import json
import time
import requests
from typing import List, Set
from collections import deque

class RateLimiter:
    """Handles API rate limiting by enforcing request limits per minute."""
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.window_size = 60  # Time window in seconds
        self.request_timestamps = deque()
    
    def wait_if_needed(self):
        """Checks if the rate limit is exceeded and waits if necessary."""
        current_time = time.time()
        while self.request_timestamps and self.request_timestamps[0] < current_time - self.window_size:
            self.request_timestamps.popleft()
        if len(self.request_timestamps) >= self.requests_per_minute:
            wait_time = self.request_timestamps[0] + self.window_size - current_time
            if wait_time > 0:
                print(f"Rate limit hit. Waiting for {wait_time:.2f} seconds.")
                time.sleep(wait_time)
        self.request_timestamps.append(time.time())

class AutocompleteAPIClient:
    """Handles API requests to fetch autocomplete suggestions."""
    def __init__(self, base_url: str = "http://35.200.185.69:8000"):
        self.base_url = base_url
        self.session = requests.Session()
    
    def get_suggestions(self, query: str) -> List[str]:
        """Fetch autocomplete results for a given query."""
        url = f"{self.base_url}/v3/autocomplete"
        params = {"query": query}
        response = self.session.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        return []

class V3Extractor:
    """Extracts names using the Autocomplete API and DFS approach."""
    def __init__(self, output_file: str):
        self.version = "v3"
        self.api_client = AutocompleteAPIClient()
        self.rate_limiter = RateLimiter(80)  # Limit of 80 requests per minute
        self.output_file = output_file
        self.names: Set[str] = set()
        self.visited_prefixes: Set[str] = set()
        self.request_count: int = 0
    
    def extract_names(self):
        """Initiates the name extraction process by iterating over possible characters."""
        for char in self.get_character_set():
            if char not in self.visited_prefixes:
                self._dfs(char)
        self._save_results()
        print(f"Extraction complete. {len(self.names)} names extracted from {self.request_count} requests.")
    
    def _dfs(self, prefix: str):
        """Performs a depth-first search to explore all possible name prefixes."""
        if prefix in self.visited_prefixes:
            return
        self.visited_prefixes.add(prefix)
        self.rate_limiter.wait_if_needed()
        suggestions = self.api_client.get_suggestions(prefix)
        self.request_count += 1
        self.names.update(suggestions)
        
        # If maximum results are returned, continue exploring deeper prefixes
        if len(suggestions) >= self.get_max_results():
            for char in self.get_character_set():
                self._dfs(prefix + char)
    
    def _save_results(self):
        """Saves extracted names and metadata to a JSON file."""
        with open(self.output_file, 'w') as f:
            json.dump({
                'version': self.version,
                'names': list(self.names),
                'request_count': self.request_count,
                'num_names': len(self.names)
            }, f, indent=2)
    
    def get_character_set(self) -> List[str]:
        """Returns a list of characters to be used in name queries."""
        return [str(i) for i in range(10)] + [chr(i) for i in range(ord('a'), ord('z') + 1)] + ['+', '-', '.']
    
    def get_max_results(self) -> int:
        """Returns the maximum number of results returned by the API."""
        return 15

def main(output_file: str):
    """Main function to initiate name extraction."""
    extractor = V3Extractor(output_file)
    extractor.extract_names()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Run V3 name extractor')
    parser.add_argument('--output-file', type=str, default='v3_names.json', help='File to store results')
    args = parser.parse_args()
    main(args.output_file)
