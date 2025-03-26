import requests
import time

def increment_query(query):
    """Move to the next valid prefix if query ends in 'z'."""
    while query and query[-1] == 'z':
        query = query[:-1]  # Reduce length
    if not query:
        return None  # Stop if nothing left
    return query[:-1] + chr(ord(query[-1]) + 1)  # Increment last non-'z' char

def fetch_names():
    time1 = time.time()
    base_url = "http://35.207.196.198:8000/v1/autocomplete"
    query = "a"  # Start query
    unique_names = set()
    request_count = 0
    
    while query:
        try:
            response = requests.get(f"{base_url}?query={query}&max_results=50", timeout=5)
            request_count += 1
            
            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                break
            
            data = response.json()
            results = data.get("results", [])
            unique_names.update(results)
            print(f"Query: {query}, Results: {len(results)}, Total Unique: {len(unique_names)}")
            
            if len(results) == 50:
                query = results[-1][:len(query) + 1]  # Expand query with last name prefix
            else:
                query = increment_query(query)  # Move to next valid prefix
            
            if not query or query > "zzzzzzzzzz": # no name was more than 10 characters long
                break
            
            time.sleep(0.5)  # Rate limiting
        
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break

    # Save results to a file
    with open("v1_names.txt", "w") as file:
        file.write(f"Total Unique Names: {len(unique_names)}\n")
        file.write(f"Total API Requests: {request_count}\n")
        file.write("Extracted Names:\n")
        file.write("\n".join(unique_names))

    print(f"Results saved to output.txt")
    time2 = time.time()

    print(f"time taken: {time2-time1} seconds\n")
    print(f"Total API Requests: {request_count}\n")
    print(f"Total Unique Names: {len(unique_names)}")

fetch_names()