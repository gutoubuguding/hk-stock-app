#!/usr/bin/env python3
"""Test LLM call directly without news fetching"""
import httpx
import time

api_key = "sk-cp-kvWu_D1285p3QaGD0wEvAzkLj4gJb_J45_9YiQmupBu5LTEd389ackr0lxxR3V_l86KO9euvMbuaRyYf62E113mK0BZl2oHCQlTuOOEQggwGj2vkG1Nm3Nk"
base_url = "https://api.minimax.chat/v1"
model = "MiniMax-M2.7"

# Simple test
prompt = "Hello, respond with 'OK' only"

payload = {
    "model": model,
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": prompt}
    ],
    "temperature": 0.7,
    "max_tokens": 50
}

headers = {
    "Authorization": f"Bearer {api_key}",
    "Content-Type": "application/json"
}

# Ensure the URL is correct
url = base_url.rstrip("/") + "/chat/completions"
print(f"Calling: {url}")

start = time.time()
try:
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, headers=headers, json=payload)
        elapsed = time.time() - start
        print(f"Status: {resp.status_code}, Time: {elapsed:.2f}s")
        print(f"Response: {resp.text[:500]}")
except Exception as e:
    elapsed = time.time() - start
    print(f"Error after {elapsed:.2f}s: {e}")

# Now test with a long prompt (similar to what the IPO analysis would send)
long_prompt = """
请分析港股新股 02476 胜宏科技 上市后的走势预期。

【最新新闻】
1. 【东方财富 | 2026-04-21】胜宏科技今日在港交所上市，首日涨幅超过50%
2. 【新浪财经 | 2026-04-21】胜宏科技是一家专注于半导体存储的公司
3. 【证券时报 | 2026-04-20】胜宏科技IPO发行价209.88港元，募资规模较大

请给出：
- 上市首日涨跌预期
- 短期走势判断
- 综合评级
"""

payload2 = {
    "model": model,
    "messages": [
        {"role": "system", "content": "你是一位专业的港股分析师，擅长分析股票新闻和新股走势。请用中文回答。"},
        {"role": "user", "content": long_prompt}
    ],
    "temperature": 0.7,
    "max_tokens": 1000
}

print("\n\nTesting with longer prompt...")
start = time.time()
try:
    with httpx.Client(timeout=30) as client:
        resp = client.post(url, headers=headers, json=payload2)
        elapsed = time.time() - start
        print(f"Status: {resp.status_code}, Time: {elapsed:.2f}s")
        print(f"Response: {resp.text[:1000]}")
except Exception as e:
    elapsed = time.time() - start
    print(f"Error after {elapsed:.2f}s: {e}")