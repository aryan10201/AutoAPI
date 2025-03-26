# Extracting Names from Autocomplete API

## Overview
This project automates the extraction of all possible names available through an undocumented autocomplete API. The solution systematically queries the API, navigates through constraints like rate limiting, and stores extracted names efficiently.

## Interesting Findinds on API Testing
**Max_results**: When we hit on "http://35.207.196.198:8000/v1/autocomplete?query=a&max_results" it gives "Input should be a valid integer, unable to parse string as an integer", basically the default results for V1, V2, V3 are 10, 12, 15 respectively but after we set max_results API gives 50, 75, 100 results respectively per query.
**Rate Limits**: It is 100, 50, 80 requests per minute from V1, V2, V3 respectively.

## Approach for V1_script.py
The extractor is implemented in Python and uses a class called AutocompleteExtractor. The main features include:
* Concurrent Requests: Uses a ThreadPoolExecutor to perform multiple queries concurrently (one for each starting letter from the provided character list).
* Recursive Prefix Exploration: For each query, if the API returns exactly the maximum allowed results, it assumes there might be additional names matching that prefix. The extractor then recursively extends the prefix to discover further results.
* Rate Limiting Handling: If the API responds with a 429 status code (indicating too many requests), the extractor waits for 30 seconds (Obtained after multiple testing of code) before retrying.
* Thread-Safe Operations: Shared data (e.g., the set of discovered names and request count) is updated in a thread-safe manner using locks.
Saving Results: Stores extracted names in **v1_names.json** with request stats

## Approach for Better_V1_script.py
Saving Results: Stores extracted names in **v1_names.txt** with request stats

## Approach for V2 & V3
Initialization: Sets up API parameters (base_url, max_results, charlist, version) and threading lock.

Querying API: Requests suggestions, handles rate limits (429), and retries on failures.

Recursive Exploration: Uses prefixes to discover names, parallelized with ThreadPoolExecutor.

Saving Results: Stores extracted names in v2_names.json & v3names.json with request stats

## API Behavior Observations & Results
| Version   | Def. Results per Query | Character Set Supported |Max_results| Rate Limit (Requests/Min) | Names Extracted | Number of Requests |Execution Time|
|-----------|----------------------  |-------------------------|-----------|-------------------------- |---------------- |------------------  |--------------|
| Better_V1 | 10                     | Lowercase Letters (a-z) | 50        | 100                       | 18,632          | 1630               |18 Min        |
| V1_Script | 10                     | Lowercase Letters (a-z) | 50        | 100                       | 18,632          | 1780               |16 Min        |
| V2        | 12                     | a-z, 0-9                | 75        | 50                        | 13,730          | 2278               |38 Min        |
| V3        | 15                     | a-z, 0-9, +, -, ., space| 100       | 80                        | 12,318          | 1951               |21 Min        |

**There are two different codes for V1, one saves time other takes less requests**

## Submission Files
- **Working Code:** `V1_Script.py`, `V2_Script.py`, `V3_Script.py`,`Better_V1_Script.py`
- **Documentation:** `README.md`
- **Extracted Data:** `v1_names.json`, `v2_names.json`, `v3_names.json`,`v1_names.txt`

## Conclusion
Through systematic API exploration, efficient request handling, and the use of concurrency (ThreadPoolExecutor), we successfully extracted names from the autocomplete system while adhering to API constraints.

