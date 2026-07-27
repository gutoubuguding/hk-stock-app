#!/usr/bin/env python3
"""Test IPO endpoint directly from Python"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
import urllib.request
import urllib.parse
import json
import time

params = {
    "stock_code": "02476",
    "stock_name": "圣诺医药",
    "api_key": "sk-cp-kvWu_D1285p3QaGD0wEvAzkLj4gJb_J45_9YiQmupBu5LTEd389ackr0lxxR3V_l86KO9euvMbuaRyYf62E113mK0BZl2oHCQlTuOOEQggwGj2vkG1Nm3Nk",
    "base_url": "https://api.minimax.chat/v1",
    "model": "MiniMax-M2.7"
}
url = "http://localhost:8081/api/analyze/ipo?" + urllib.parse.urlencode(params)

print(f"Calling AI service directly...")
start = time.time()
try:
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=25) as resp:
        elapsed = time.time() - start
        data = json.loads(resp.read())
        print(f"Success in {elapsed:.1f}s!")
        print(f"news_count: {data.get('news_count',0)}")
        print(f"analysis_len: {len(data.get('analysis',''))}")
        if data.get('error'):
            print(f"error: {data.get('error')}")
except Exception as e:
    elapsed = time.time() - start
    print(f"Failed after {elapsed:.1f}s: {type(e).__name__}: {e}")