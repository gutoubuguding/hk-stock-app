import httpx

# Test the backend IPO AI analysis endpoint
url = "http://localhost:8080/api/ipo/ai-analysis/02476"

print("Testing backend IPO AI analysis endpoint...")
try:
    with httpx.Client(timeout=10) as client:
        resp = client.get(url)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

# Also test the IPO comparison endpoint to see if it returns data
print("\nTesting IPO comparison endpoint...")
try:
    with httpx.Client(timeout=10) as client:
        resp = client.get("http://localhost:8080/api/ipo/comparison")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Total: {data.get('total', 'N/A')}")
            if 'data' in data and len(data['data']) > 0:
                print(f"First item: {data['data'][0]}")
except Exception as e:
    print(f"Error: {e}")