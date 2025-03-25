# Extracting Names from Autocomplete API

## Overview
This project automates the extraction of all possible names available through an undocumented autocomplete API. The solution systematically queries the API, navigates through constraints like rate limiting, and stores extracted names efficiently.

## Key Features & Approach
Asynchronous Requests: Utilizes Python's asyncio and aiohttp libraries for concurrent network requests, significantly improving performance.

Depth-First Search (DFS) Approach: Uses DFS to explore autocomplete suggestions by starting with single-letter prefixes and expanding recursively.

Rate Limit Management: Implements automatic retries with a 10-second delay when encountering a 429 rate limit response.

Max Results Handling: If the API returns the maximum number of results, the extractor extends the current prefix and continues the search.

Prefix Crawling Strategy: Recursively explores prefixes (e.g., a, aa, ab, etc.) to extract all available names.

Efficient Data Storage: Uses a set to store unique names, preventing duplicates and ensuring accurate results.

## API Behavior Observations
| Version | Max Results per Query | Character Set Supported |Max_results| Rate Limit (Requests/Min) | Names Extracted | Number of Requests |
|---------|---------------------- |-------------------------|-----------|-------------------------- |---------------- |------------------  |
| V1      | 10                    | Lowercase Letters (a-z) | 50        | 100                       | 18,632          | 17259              |
| V2      | 12                    | a-z, 0-9                | 75        | 50                        | 13,730          | 7416               |
| V3      | 15                    | a-z, 0-9, +, -, ., space| 100       | 80                        | 12,226          | 3393               |

## Submission Files
- **Working Code:** `V1_Script.py`, `V2_Script.py`, `V3_Script.py`
- **Documentation:** `README.md`
- **Extracted Data:** `v1_names.json`, `v2_names.json`, `v3_names.json`

## Conclusion
Through systematic API exploration, efficient request handling, and the use of concurrency, we successfully extracted names from the autocomplete system while adhering to API constraints.

