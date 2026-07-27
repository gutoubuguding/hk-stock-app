import httpx
import time

# Test the AI service IPO endpoint directly
url = "http://localhost:8083/api/analyze/ipo"
params = {
    "stock_code": "02476",
    "stock_name": "胜宏科技",
    "api_key": "sk-cp-kvWu_D1285p3QaGD0wEvAzkLj4gJb_J45_9YiQmupBu5LTEd389ackr0lxxR3V_l86KO9euvMbuaRyYf62E113mK0BZl2oHCQlTuOOEQggwGj2vkG1Nm3Nk",
    "base_url": "https://api.minimax.chat/v1",
    "model": "MiniMax-M2.7"
}

print("Testing AI service IPO endpoint directly...")
start = time.time()
try:
    with httpx.Client(timeout=120) as client:
        resp = client.get(url, params=params)
        elapsed = time.time() - start
        print(f"Status: {resp.status_code}, Time: {elapsed:.2f}s")
        print(f"Response: {resp.text[:2000]}")
except Exception as e:
    elapsed = time.time() - start
    print(f"Error after {elapsed:.2f}s: {e}")