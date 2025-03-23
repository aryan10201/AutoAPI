import aiohttp
import asyncio
import time
import string
from collections import deque
import json  

BASE_URL = "http://35.200.185.69:8000/v1/autocomplete?query="
HEADERS = {"User-Agent": "Mozilla/5.0"}

INITIAL_WAIT = 0.2
MAX_WAIT = 5
OUTPUT_FILE = "v1_names.json" 

rate_limit_wait = INITIAL_WAIT
visited_queries = set()
found_names = set()
total_requests = 0

async def fetch_names(session, query):
    global rate_limit_wait, total_requests
    url = BASE_URL + query
    
    while True:
        try:
            async with session.get(url, headers=HEADERS) as response:
                total_requests += 1
                if response.status == 429:
                    rate_limit_wait = min(rate_limit_wait * 1.5, MAX_WAIT)
                    print(f"[429] Rate limit. Sleeping {rate_limit_wait:.1f}s ... (query='{query}')")
                    await asyncio.sleep(rate_limit_wait)
                    continue
                data = await response.json()
                rate_limit_wait = max(rate_limit_wait * 0.8, INITIAL_WAIT)
                return data.get("results", [])
        except Exception as e:
            print(f"Error fetching {query}: {e}. Retrying in 2s...")
            await asyncio.sleep(2)

async def explore_query(session, query, queue):
    if query in visited_queries:
        return
    visited_queries.add(query)
    
    results = await fetch_names(session, query)
    if not results:
        return
    
    for name in results:
        found_names.add(name)
    
    if len(results) == 10:
        last_name = results[-1]
        if len(last_name) > len(query):
            pivot_char = last_name[len(query)]
            start_ord = ord(pivot_char)
            end_ord = ord('z')
            for c in range(start_ord, end_ord + 1):
                next_query = query + chr(c)
                if next_query not in visited_queries:
                    queue.append(next_query)

async def explore_names():
    # initial BFS queue with "aa".."zz"
    queue = deque(a + b for a in string.ascii_lowercase for b in string.ascii_lowercase)
    concurrency_limit = asyncio.Semaphore(5)

    async with aiohttp.ClientSession() as session:
        tasks = []
        while queue or tasks:
            while queue and len(tasks) < 5:
                query = queue.popleft()
                task = asyncio.create_task(worker(session, query, queue, concurrency_limit))
                tasks.append(task)
            if tasks:
                done, pending = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
                tasks = list(pending)
    
    output_data = {
        "total_requests": total_requests,
        "total_names": len(found_names),
        "names": sorted(found_names)
    }
    
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    
    print(f"\nTotal unique names collected: {len(found_names)}")
    print(f"Total API requests made: {total_requests}")

async def worker(session, query, queue, semaphore):
    async with semaphore:
        await explore_query(session, query, queue)

if __name__ == "__main__":
    start_time = time.time()
    asyncio.run(explore_names())
    print("--- %s seconds ---" % (time.time() - start_time))