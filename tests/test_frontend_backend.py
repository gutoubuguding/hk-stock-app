import httpx

# Test if the frontend proxy is working correctly
# Test backend IPO AI endpoint via localhost:8080 (how the built frontend accesses it)
print("=== Test via Backend (port 8080) ===")
url = "http://localhost:8080/api/ipo/ai-analysis/02476"
with httpx.Client(timeout=120) as client:
    resp = client.get(url)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    if "error" in data:
        print(f"Error: {data['error']}")
    elif "analysis" in data:
        analysis = data.get("analysis", "")
        if "LLM" in analysis or "失败" in str(analysis):
            print(f"LLM Failed: {analysis[:200]}")
        else:
            print(f"Success! Analysis length: {len(analysis)}")

# Test the config endpoint to make sure API key is loaded
print("\n=== Test Config Endpoint ===")
with httpx.Client(timeout=10) as client:
    resp = client.get("http://localhost:8080/api/config/current")
    print(f"Config status: {resp.status_code}")
    if resp.status_code == 200:
        data = resp.json()
        print(f"AI Provider: {data.get('ai_provider')}")
        print(f"AI Model: {data.get('ai_model')}")
        api_key = data.get('ai_api_key', '')
        print(f"API Key: {api_key[:15]}...{api_key[-5:] if len(api_key) > 20 else ''}")