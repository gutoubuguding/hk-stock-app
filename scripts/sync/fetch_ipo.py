#!/usr/bin/env python3
"""从东方财富获取港股IPO数据 2025-01-01至今"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False

import psycopg2
import json
from datetime import datetime

conn = psycopg2.connect(
    host="localhost", port=5432, database="hk_stock",
    user="postgres", password="pc20050218"
)
cur = conn.cursor()

print("Fetching HK IPO data from EastMoney...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://data.eastmoney.com/"
}

# 东方财富港股新股接口
url = "https://datacenter-web.eastmoney.com/api/data/v1/get"
params = {
    "sortColumns": "LISTING_DATE",
    "sortTypes": "-1",
    "pageSize": 200,
    "pageNumber": 1,
    "reportName": "RPT_IPO_HKAPPLY",
    "columns": "ALL",
    "quoteColumns": "",
    "filter": '(LISTING_DATE>="2025-01-01")'
}

try:
    resp = requests.get(url, params=params, headers=headers, timeout=15)
    data = resp.json()
    
    if data.get("result") and data["result"].get("data"):
        items = data["result"]["data"]
        print(f"Got {len(items)} IPO records")
        
        # 打印第一条数据看看结构
        if items:
            print(f"\nSample record keys: {list(items[0].keys())}")
            print(f"Sample: {json.dumps(items[0], ensure_ascii=False)[:500]}")
        
    else:
        print(f"No data. Response: {json.dumps(data, ensure_ascii=False)[:500]}")
        
except Exception as e:
    print(f"Error: {e}")

cur.close()
conn.close()
