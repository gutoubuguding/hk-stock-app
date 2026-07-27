#!/usr/bin/env python3
"""Test news fetch for 02476 specifically with timing"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
import time

sys.path.insert(0, r'C:\Users\34596\.openclaw\workspace\hk-stock-app\ai-service')
from app.routers.analyze import fetch_stock_news

print("Testing news fetch for 02476 圣诺医药...")

# Test with days=7 (what IPO analyze uses)
start = time.time()
news = fetch_stock_news(stock_name="圣诺医药", stock_code="02476", days=7)
elapsed = time.time() - start

print(f"News count: {len(news)}")
print(f"Time: {elapsed:.1f}s")
for i, n in enumerate(news[:5]):
    print(f"  {i+1}. [{n['source']} | {n['date']}] {n['title'][:60]}")

# Also test with None name and days=1
print("\nTesting with stock_code only and days=1...")
start2 = time.time()
news2 = fetch_stock_news(stock_code="02476", days=1)
elapsed2 = time.time() - start2
print(f"News count: {len(news2)}, Time: {elapsed2:.1f}s")