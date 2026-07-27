#!/usr/bin/env python3
"""Test news fetching speed"""
import httpx
import time
from bs4 import BeautifulSoup

def fetch_from_google_news(keyword, stock_code, days=7):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    queries = []
    if stock_code:
        queries.append(f'"{stock_code}" {keyword} 港股')
    queries.append(f'{keyword} 港股 股票')
    
    for query in queries:
        try:
            import urllib.parse
            encoded_query = urllib.parse.quote_plus(query)
            url = f"https://news.google.com/rss/search?hl=zh-CN&gl=CN&ceid=CN:zh-Hans&q={encoded_query}"
            
            start = time.time()
            with httpx.Client(timeout=10, follow_redirects=True) as client:
                resp = client.get(url, headers=headers)
                elapsed = time.time() - start
                print(f"Google News query '{query[:30]}...' - Status: {resp.status_code}, Time: {elapsed:.2f}s")
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "lxml-xml")
                    items = soup.find_all("item", limit=3)
                    print(f"  Found {len(items)} items")
                    return True
        except Exception as e:
            print(f"Google News query failed: {e}")
    return False

def fetch_from_sina(stock_code, stock_name, days=7):
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://finance.sina.com.cn/"}
    hk_code = stock_code.zfill(5)
    url = f"https://feed.mix.sina.com.cn/api/roll/get"
    params = {"pageid": "153", "lid": "2516", "k": f"{hk_code} {stock_name}".strip(), "num": 10, "page": 1, "r": 0.5}
    
    start = time.time()
    try:
        with httpx.Client(timeout=10, follow_redirects=True) as client:
            resp = client.get(url, params=params, headers=headers)
            elapsed = time.time() - start
            print(f"Sina news - Status: {resp.status_code}, Time: {elapsed:.2f}s")
            if resp.status_code == 200:
                data = resp.json()
                if "result" in data and "data" in data["result"]:
                    print(f"  Found {len(data['result']['data'])} items")
                    return True
    except Exception as e:
        print(f"Sina news failed: {e}")
    return False

def fetch_from_eastmoney(keyword, stock_code, days=7):
    headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://so.eastmoney.com/"}
    search_keyword = f"{stock_code} {keyword}".strip() if stock_code else keyword
    url = "https://search-api-web.eastmoney.com/api/search/get"
    params = {"keyword": search_keyword, "type": "cmsArticle", "pageIndex": 1, "pageSize": 10, "client": "web", "clientType": "web", "clientVersion": "curr"}
    
    start = time.time()
    try:
        with httpx.Client(timeout=10) as client:
            resp = client.get(url, params=params, headers=headers)
            elapsed = time.time() - start
            print(f"Eastmoney search - Status: {resp.status_code}, Time: {elapsed:.2f}s")
            if resp.status_code == 200:
                data = resp.json()
                if "result" in data:
                    print(f"  Found some results")
                    return True
    except Exception as e:
        print(f"Eastmoney search failed: {e}")
    return False

# Test news fetching
print("Testing news sources for '胜宏科技' (02476):\n")
fetch_from_google_news("胜宏科技", "02476")
print()
fetch_from_sina("02476", "胜宏科技")
print()
fetch_from_eastmoney("胜宏科技", "02476")