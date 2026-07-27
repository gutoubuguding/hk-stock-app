#!/usr/bin/env python3
"""Quick test AI service IPO endpoint"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
import urllib.request
import urllib.parse
import json

params = {
    "stock_code": "02476",
    "stock_name": "圣诺医药",
    "api_key": "sk-cp-kvWu_D1285p3QaGD0wEvAzkLj4gJb_J45_9YiQmupBu5LTEd389ackr0lxxR3V_l86KO9euvMbuaRyYf62E113mK0BZl2oHCQlTuOOEQggwGj2vkG1Nm3Nk",
    "base_url": "https://api.minimax.chat/v1",
    "model": "MiniMax-M2.7"
}

url = "http://localhost:8081/api/analyze/ipo?" + urllib.parse.urlencode(params)
print(f"URL: {url[:80]}...")

req = urllib.request.Request(url)
try:
    with urllib.request.urlopen(req, timeout=20) as resp:
        data = json.loads(resp.read())
        print(f"Success!")
        print(f"  Analysis length: {len(data.get('analysis', ''))}")
        print(f"  News count: {data.get('news_count', 0)}")
        print(f"  Error: {data.get('error', 'none')}")
        if data.get('analysis'):
            print(f"  First 200 chars of analysis: {data['analysis'][:200]}")
except Exception as e:
    print(f"Failed: {type(e).__name__}: {e}")