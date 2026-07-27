#!/usr/bin/env python3
"""Test different stocks to see if 02476 is special"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
import urllib.request
import urllib.parse
import json
import time

API_KEY = "sk-cp-kvWu_D1285p3QaGD0wEvAzkLj4gJb_J45_9YiQmupBu5LTEd389ackr0lxxR3V_l86KO9euvMbuaRyYf62E113mK0BZl2oHCQlTuOOEQggwGj2vkG1Nm3Nk"
BASE_URL = "https://api.minimax.chat/v1"
MODEL = "MiniMax-M2.7"

stocks = [
    ("00700", "腾讯"),
    ("02476", "圣诺医药"),
    ("06060", "医脉通"),
]

for code, name in stocks:
    params = {
        "stock_code": code,
        "stock_name": name,
        "api_key": API_KEY,
        "base_url": BASE_URL,
        "model": MODEL
    }
    url = "http://localhost:8081/api/analyze/ipo?" + urllib.parse.urlencode(params)
    
    print(f"\nTesting {code} {name}...")
    req = urllib.request.Request(url)
    start = time.time()
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            elapsed = time.time() - start
            data = json.loads(resp.read())
            analysis = data.get('analysis', '')
            print(f"  Success in {elapsed:.1f}s: news={data.get('news_count',0)}, analysis_len={len(analysis)}, error={data.get('error','none')}")
    except Exception as e:
        elapsed = time.time() - start
        print(f"  Failed after {elapsed:.1f}s: {type(e).__name__}: {e}")