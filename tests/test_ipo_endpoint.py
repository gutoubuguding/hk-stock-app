import httpx
import json

# Test the IPO endpoint with a short timeout
url = "http://localhost:8082/api/analyze/ipo"
params = {
    "stock_code": "02476",
    "stock_name": "胜宏科技",
    "api_key": "sk-cp-kvWu_D1285p3QaGD0wEvAzkLj4gJb_J45_9YiQmupBu5LTEd389ackr0lxxR3V_l86KO9euvMbuaRyYf62E113mK0BZl2oHCQlTuOOEQggwGj2vkG1Nm3Nk",
    "base_url": "https://api.minimax.chat/v1",
    "model": "MiniMax-M2.7"
}

print("Testing IPO analysis endpoint...")
try:
    with httpx.Client(timeout=60) as client:
        resp = client.get(url, params=params)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.text[:1000]}")
except Exception as e:
    print(f"Error: {e}")