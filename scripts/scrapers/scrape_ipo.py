#!/usr/bin/env python3
"""从港交所获取2025年至今的新股列表"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False
import json

# 港交所新股数据API
# https://www.hkex.com.hk/Services/Trading/Securities/Securities-Lists/Newly-Listed-Securities?sc_lang=zh-HK

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json"
}

# 尝试港交所API
urls_to_try = [
    "https://www1.hkexnews.hk/ncms/json/eds/newlisted_securities_main.json",
    "https://www.hkex.com.hk/services/trading/securities/securitieslists/newlistedsecurities_json",
    "https://www.hkex.com.hk/Services/Trading/Securities/Securities-Lists/Newly-Listed-Securities/data.json",
]

for url in urls_to_try:
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f"URL: {url}")
        print(f"Status: {resp.status_code}")
        if resp.status_code == 200:
            try:
                data = resp.json()
                print(f"Data: {json.dumps(data, ensure_ascii=False)[:500]}")
            except:
                print(f"Content: {resp.text[:500]}")
        print()
    except Exception as e:
        print(f"Error: {e}")
        print()

# 尝试东方财富港股新股列表
print("=== Trying EastMoney HK IPO ===")
em_url = "https://push2.eastmoney.com/api/qt/clist/get"
em_params = {
    "pn": 1,
    "pz": 200,
    "po": 1,
    "np": 1,
    "ut": "bd1d9ddb04089700cf9c27f6f7426281",
    "fltt": 2,
    "invt": 2,
    "fid": "f26",  # 上市日期
    "fs": "m:128+t:3,m:128+t:4,m:128+t:1,m:128+t:2",  # 港股
    "fields": "f12,f14,f26,f27",  # 代码,名称,上市日期,发行价
}

try:
    resp = requests.get(em_url, params=em_params, headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    data = resp.json()
    if data.get("data") and data["data"].get("diff"):
        items = data["data"]["diff"]
        print(f"Got {len(items)} items")
        # 显示前几条
        for item in items[:5]:
            print(f"  {item}")
    else:
        print(f"Response: {json.dumps(data, ensure_ascii=False)[:500]}")
except Exception as e:
    print(f"Error: {e}")
