# Extracting Names from Autocomplete API

## Overview
This project automates the extraction of all possible names available through an undocumented autocomplete API. The solution systematically queries the API, navigates through constraints like rate limiting, and stores extracted names efficiently.

## Approach
### **Version 1 (V1)**
- Explored API using simple queries like `aa`to `zz`, etc.
- Discovered that the maximum results per query were **10**.
- API had a **rate limit** of **100 requests per minute**.
- Implemented a **Breadth-First Search (BFS)** approach to traverse through name possibilities.
- Used **async concurrent workers using semaphore** to reduce execution time.
- Saved extracted names in `v1_names.json`.
- **Script:** `V1_Script.py`

### **Version 2 (V2)**
- API updated to include **digits (0-9)** in names.
- Discovered that the maximum results per query were **12**.
- The API had a stricter **rate limit of 50 requests per minute**.
- Modified BFS to include **alphanumeric prefixes**.
- Implemented **exponential backoff** for handling rate limits.
- Implemented **periodic saving** to prevent data loss.
- Saved extracted names in `v2_names.json`.
- **Script:** `V2_Script.py`

### **Version 3 (V3)**
- API extended to support **special characters (+, -, ., space)**.
- Discovered that the maximum results per query were **15**.
- API had a **rate limit** of **80 requests per minute**.
- Implemented **adaptive retries with exponential backoff** to handle **rate limits (HTTP 429 errors)**.
- Implemented **progress saving** every **100 requests**.
- Ensured **URL encoding** to handle spaces correctly.
- Extracted names are stored in `v3_names.json`.
- **Script:** `V3_Script.py`

## API Behavior Observations
| Version | Max Results per Query | Character Set Supported | Rate Limit (Requests/Min) | Names Extracted | Number of Requests |
|---------|---------------------- |-------------------------|-------------------------- |---------------- |------------------  |
| V1      | 10                    | Lowercase Letters (a-z) | 100                       | 18,632          | 17259              |
| V2      | 12                    | a-z, 0-9                | 50                        | 13,730          | 7416               |
| V3      | 15                    | a-z, 0-9, +, -, ., space| 80                        | 12,226          | 3393               |

## V1 Analysis
| Version | Number of Workers | Number of Requests |Time Taken to Complete Script|
|---------|-------------------|--------------------|-----------------------------|
| V1      | 10                | ~20000             | ~49 minutes                 |
| V1      | 5                 | 17259              | ~67 minutes                 |
| V1      | 3                 | 15971              | ~90 minutes                 |
**Make changes in the V1_Script to obtain these results**

## Features
- **Automated BFS-based name extraction** to ensure all possible names are collected.
- **Handles rate limits** using **adaptive waiting, exponential backoff, and retry mechanisms**.
- **Uses async concurrent workers, semaphore** to reduce execution time.
- **Progress persistence** to avoid redundant requests in case of failures.
- **Efficient character expansion** to explore names systematically.
- **Extracted names saved in JSON files** for easy access.

## Submission Files
- **Working Code:** `V1_Script.py`, `V2_Script.py`, `V3_Script.py`
- **Documentation:** `README.md`
- **Extracted Data:** `v1_names.json`, `v2_names.json`, `v3_names.json`

## Conclusion
Through systematic API exploration, efficient request handling, and the use of concurrency, we successfully extracted names from the autocomplete system while adhering to API constraints.

