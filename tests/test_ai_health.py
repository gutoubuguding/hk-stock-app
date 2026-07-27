import httpx

# Test health endpoint
try:
    with httpx.Client(timeout=5) as client:
        resp = client.get("http://localhost:8082/health")
        print(f"Health: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"Health error: {e}")

# Test root endpoint
try:
    with httpx.Client(timeout=5) as client:
        resp = client.get("http://localhost:8082/")
        print(f"Root: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"Root error: {e}")