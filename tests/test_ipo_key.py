#!/usr/bin/env python3
"""Test IPO endpoint with minimal news"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
import urllib.request
import urllib.parse
import json

# Test IPO with fake api key - should fail fast with API key error, not timeout
params = {
    "stock_code": "02476",
    "stock_name": "test",
    "api_key": "invalid_key_test_only",
    "base_url": "https://api.minimax.chat/v1",
    "model": "MiniMax-M2.7"
}
url = "http://localhost:8081/api/analyze/ipo?" + urllib.parse.urlencode(params)

print(f"Testing IPO endpoint (should return quickly with key error)...")
print(f"URL: {url[:80]}...")

req = urllib.request.Request(url)
try:
    with urllib.request.urlopen(req, timeout=25) as resp:
        data = json.loads(resp.read())
        print(f"Success! analysis={data.get('analysis','')[:100] if data.get('analysis') else 'empty'}")
        print(f"error={data.get('error','none')}")
        print(f"news_count={data.get('news_count',0)}")
except Exception as e:
    print(f"Failed: {type(e).__name__}: {e}")