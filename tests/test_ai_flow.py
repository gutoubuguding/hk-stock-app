import httpx

# Test the backend IPO AI analysis endpoint with the new config
url = "http://localhost:8080/api/ipo/ai-analysis/02476"

print("Testing backend IPO AI analysis endpoint...")
try:
    with httpx.Client(timeout=90) as client:
        resp = client.get(url)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:1500]}")
except Exception as e:
    print(f"Error: {e}")