#!/usr/bin/env python3
"""Debug IPO news fetch timing"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
import time

# Import the function
sys.path.insert(0, r'C:\Users\34596\.openclaw\workspace\hk-stock-app\ai-service')
from app.routers.analyze import fetch_stock_news

print("Testing fetch_stock_news for 02476...")
start = time.time()

# Test with minimal days
try:
    news = fetch_stock_news(stock_name="test", stock_code="02476", days=1)
    elapsed = time.time() - start
    print(f"Test with 'test' name: {elapsed:.1f}s, {len(news)} news")
except Exception as e:
    elapsed = time.time() - start
    print(f"Test with 'test' failed: {elapsed:.1f}s - {e}")

# Test with actual name
start2 = time.time()
try:
    news2 = fetch_stock_news(stock_name="圣诺医药", stock_code="02476", days=1)
    elapsed2 = time.time() - start2
    print(f"Test with '圣诺医药': {elapsed2:.1f}s, {len(news2)} news")
except Exception as e:
    elapsed2 = time.time() - start2
    print(f"Test with '圣诺医药' failed: {elapsed2:.1f}s - {e}")