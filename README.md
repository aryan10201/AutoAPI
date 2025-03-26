![image](https://github.com/user-attachments/assets/86bbc32f-7cb5-4d75-8402-fc85665121bf)
![image](https://github.com/user-attachments/assets/c7ac2dd5-e7e3-46f6-bcfb-28c74305420d)
![image](https://github.com/user-attachments/assets/ea90c9c0-d5ac-45f7-aff6-d95093a5b55f)
# Extracting Names from Autocomplete API

## Overview
This project automates the extraction of all possible names available through an undocumented autocomplete API. The solution systematically queries the API, navigates through constraints like rate limiting, and stores extracted names efficiently.

## Interesting Findinds on API Testing
**Max_results**: When we hit on "http://35.207.196.198:8000/v1/autocomplete?query=a&max_results" it gives "Input should be a valid integer, unable to parse string as an integer", basically the default results for V1, V2, V3 are 10, 12, 15 respectively but after we set max_results API gives 50, 75, 100 results respectively per query.

**Rate Limits**: It is 100, 50, 80 requests per minute from V1, V2, V3 respectively.

## Approach for V1_script.py, V2 & V3
The extractor is implemented in Python and uses DFS logic & Concurrency to extract names. The main features include:

* Concurrent Requests: Uses a **ThreadPoolExecutor** to perform multiple queries concurrently (one for each starting letter from the provided character list) to save time.
* Recursive Prefix Crawling: For each query, if the API returns exactly the maximum allowed results, it assumes there might be additional names matching that prefix. The extractor then recursively extends the prefix to discover further results.
* Rate Limiting Handling: If the API responds with a 429 status code (indicating too many requests), the extractor waits for 30 seconds (Obtained after multiple testing of code) before retrying.
* Thread-Safe Operations: Shared data (e.g., the set of discovered names and request count) is updated in a thread-safe manner using locks.

Saving Results: Stores extracted names in **v1/v2/v3_names.json** with request stats

## Approach for Better_V1_script.py
The script fetch_names.py is designed such that it **never hits** the Rate Limit:

* Iterative Querying: Starts with a simple query ("a") and progressively generates new queries to explore the autocomplete suggestions.
* Prefix Expansion: If the API returns the maximum number of results, it intelligently expands the current query using the last returned suggestion as a basis for the next prefix.
* Rate Limiting: Incorporates a delay of 0.5s between API requests to respect rate limits and avoid overloading the server.
  **Calculation of Delay**: 100 req/min means we can send requests every 0.6s without hitting the rate limit
                            It takes approx 24s to recieve data from 100 req (0.24s/req)
                            So, Delay => 0.6s-0.24s = 0.36s (We took 0.5s to be on the safe side)
* Error Handling: Includes basic error handling for API requests to gracefully manage network issues or server errors.
* Result Saving: Saves the discovered names, along with request statistics, to a text file **v1_names.txt**

## API Behavior Observations & Results
| Version   | Def. Results per Query | Character Set Supported |Max_results| Rate Limit (Requests/Min) | Names Extracted | Number of Requests |Execution Time|
|-----------|----------------------  |-------------------------|-----------|-------------------------- |---------------- |------------------  |--------------|
| Better_V1 | 10                     | Lowercase Letters (a-z) | 50        | 100                       | 18,632          | 1630               |18 Min        |
| V1_Script | 10                     | Lowercase Letters (a-z) | 50        | 100                       | 18,632          | 1780               |16 Min        |
| V2        | 12                     | a-z, 0-9                | 75        | 50                        | 13,730          | 2278               |38 Min        |
| V3        | 15                     | a-z, 0-9, +, -, ., space| 100       | 80                        | 12,318          | 1951               |21 Min        |

**There are two different codes for V1, one saves time other takes less requests**

## Tools used
**json**: Serializes the set of extracted names and metadata (e.g., total requests) into a JSON file for structured output.

**string**: Provides useful constants like `string.ascii_lowercase` to generate a sorted list of characters for constructing query prefixes.

**threading**: Implements thread-safe operations using `threading.Lock` to protect shared variables (like the set of names and request count) from concurrent access issues.

**concurrent.futures (ThreadPoolExecutor, as_completed)**: 
  - Enables concurrent processing of multiple query prefixes.
  - Reduces total runtime by allowing parallel API calls.

**urllib.parse (quote)**: Encodes query parameters to ensure they are URL-safe when sending HTTP requests.

**typing (Literal)**: Provides static type hints to enforce valid API version values (e.g., `"v1"`, `"v2"`, `"v3"`) for clarity and reliability.

## Submission Files
- **Working Code:** `V1_Script.py`, `V2_Script.py`, `V3_Script.py`,`Better_V1_Script.py`
- **Documentation:** `README.md`
- **Extracted Data:** `v1_names.json`, `v2_names.json`, `v3_names.json`,`v1_names.txt`

## Conclusion
Through systematic API exploration, efficient request handling, and the use of concurrency (ThreadPoolExecutor), we successfully extracted names from the autocomplete system while adhering to API constraints.

