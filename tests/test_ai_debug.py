#!/usr/bin/env python3
"""测试完整的AI分析流程"""
import httpx
import time

API_KEY = "sk-cp-kvWu_D1285p3QaGD0wEvAzkLj4gJb_J45_9YiQmupBu5LTEd389ackr0lxxR3V_l86KO9euvMbuaRyYf62E113mK0BZl2oHCQlTuOOEQggwGj2vkG1Nm3Nk"
BASE_URL = "https://api.minimax.chat/v1"
MODEL = "MiniMax-M2.7"

# Test 1: Direct API call
print("=== Test 1: Direct MiniMax API ===")
payload = {
    "model": MODEL,
    "messages": [
        {"role": "system", "content": "你是一位专业的港股分析师。"},
        {"role": "user", "content": "用一句话评价茅台股票"}
    ],
    "temperature": 0.7,
    "max_tokens": 100
}
headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
url = BASE_URL.rstrip("/") + "/chat/completions"

start = time.time()
with httpx.Client(timeout=30) as client:
    resp = client.post(url, headers=headers, json=payload)
    elapsed = time.time() - start
    print(f"Status: {resp.status_code}, Time: {elapsed:.2f}s")
    data = resp.json()
    if "choices" in data and len(data["choices"]) > 0:
        content = data["choices"][0]["message"]["content"]
        print(f"Content: {content[:200]}")
    else:
        print(f"Response: {resp.text[:500]}")

# Test 2: AI service endpoint
print("\n=== Test 2: AI Service IPO endpoint ===")
service_url = "http://localhost:8083/api/analyze/ipo"
params = {
    "stock_code": "02476",
    "stock_name": "胜宏科技",
    "api_key": API_KEY,
    "base_url": BASE_URL,
    "model": MODEL
}

start = time.time()
with httpx.Client(timeout=120) as client:
    resp = client.get(service_url, params=params)
    elapsed = time.time() - start
    print(f"Status: {resp.status_code}, Time: {elapsed:.2f}s")
    data = resp.json()
    if "error" in data:
        print(f"Error: {data['error']}")
    elif "analysis" in data:
        analysis = data["analysis"]
        if "LLM" in analysis or "失败" in analysis or "失败" in analysis:
            print(f"LLM Failed: {analysis[:300]}")
        else:
            print(f"Success! Analysis length: {len(analysis)}")
            print(f"First 200 chars: {analysis[:200]}")
    else:
        print(f"Response: {str(data)[:500]}")

# Test 3: Backend IPO AI endpoint
print("\n=== Test 3: Backend IPO AI endpoint ===")
backend_url = "http://localhost:8080/api/ipo/ai-analysis/02476"

start = time.time()
with httpx.Client(timeout=130) as client:
    resp = client.get(backend_url)
    elapsed = time.time() - start
    print(f"Status: {resp.status_code}, Time: {elapsed:.2f}s")
    data = resp.json()
    if "error" in data:
        print(f"Error: {data['error']}")
    elif "analysis" in data:
        analysis = data.get("analysis", "")
        print(f"Analysis present, length: {len(analysis)}")
        if "LLM" in analysis or "失败" in str(analysis):
            print(f"LLM Failed content: {analysis[:300]}")
    else:
        print(f"Response keys: {list(data.keys())}")