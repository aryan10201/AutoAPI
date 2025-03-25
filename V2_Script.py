import aiohttp
import asyncio
import time
import string
import json
from typing import Literal
from urllib.parse import quote

class AsyncAutocompleteExtractor:
    def __init__(self, base_url: str, max_results: int, charlist: str, version: Literal["v1", "v2", "v3"]):
        self.api_url = base_url
        self.limit = max_results
        self.discovered_entries = set()
        self.request_total = 0
        self.characters = sorted(charlist)
        self.api_version = version
        self.req_semaphore = asyncio.Semaphore(3)  # Limit concurrent requests

    async def fetch_suggestions(self, session, search_term: str):
        encoded_term = quote(search_term)
        url = f"{self.api_url}/{self.api_version}/autocomplete?query={encoded_term}&max_results={self.limit}"

        async with self.req_semaphore:
            try:
                async with session.get(url) as resp:
                    self.request_total += 1

                    if resp.status == 429:
                        print("Rate limit reached. Pausing for 10s...")
                        await asyncio.sleep(10)
                        return await self.fetch_suggestions(session, search_term)

                    if resp.status != 200:
                        print(f"Unexpected status: {resp.status}. Retrying...")
                        await asyncio.sleep(1)
                        return []

                    response_data = await resp.json()

                    if isinstance(response_data.get("results"), list):
                        suggestions = response_data["results"]
                        print(f"Search '{search_term}' returned {len(suggestions)} results. Total found: {len(self.discovered_entries)}")
                        return suggestions
                    else:
                        print(f"Unexpected data format: {response_data.keys()}")
                        return []
            except Exception as err:
                print(f"Error with query '{search_term}': {err}")
                return []

    async def initiate_extraction(self):
        print(f"Starting extraction with max results = {self.limit}")
        start_time = time.time()

        tasks = []
        async with aiohttp.ClientSession() as session:
            for character in self.characters:
                if character == " ":
                    continue
                tasks.append(asyncio.create_task(self.analyze_prefix(session, character)))

            await asyncio.gather(*tasks)

        elapsed_time = time.time() - start_time
        print(f"Extraction completed in {elapsed_time:.2f} sec")
        print(f"Total API calls: {self.request_total}")
        print(f"Total unique entries: {len(self.discovered_entries)}")

        return self.discovered_entries

    async def analyze_prefix(self, session, prefix: str):
        print(f"Examining prefix: '{prefix}'")
        suggestions = await self.fetch_suggestions(session, prefix)

        for entry in suggestions:
            self.discovered_entries.add(entry)

        if len(suggestions) == self.limit:
            next_char = suggestions[-1][len(prefix)]
            index = self.characters.index(next_char)
            for next_char in self.characters[index:]:
                if next_char == " ":
                    continue
                await self.analyze_prefix(session, prefix + next_char)

    def store_results(self, filename="v5_names.json"):
        output_data = {
            "request_count": self.request_total,
            "total_entries": len(self.discovered_entries),
            "entries": sorted(self.discovered_entries),
        }
        with open(filename, "w") as file:
            json.dump(output_data, file, indent=2)
        print(f"Data stored in {filename}")

async def main():
    extractor = AsyncAutocompleteExtractor(
        "http://35.207.196.198:8000", 75, string.ascii_lowercase + string.digits, "v2"
    )
    extracted_entries = await extractor.initiate_extraction()
    extractor.store_results()
    print(f"Process completed. Found {len(extracted_entries)} unique entries.")
    print(f"Total API calls made: {extractor.request_total}")

if __name__ == "__main__":
    asyncio.run(main())
