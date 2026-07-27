#!/usr/bin/env python3
"""从经济通获取港股IPO数据"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# 经济通港股IPO页面
urls = [
    "https://www.etnet.com.hk/www/tc/stocks/ci_ipo_list.php",
    "https://www.aastocks.com/tc/ipo/listedipo.aspx",
    "https://www.hkipo.com/ipo/list",
]

for url in urls:
    try:
        print(f"Trying: {url}")
        resp = requests.get(url, headers=headers, timeout=15)
        print(f"Status: {resp.status_code}")
        print(f"Content length: {len(resp.text)}")
        
        # 尝试解析HTML找股票代码
        import re
        
        # 查找港股代码格式 (5位数字)
        codes = re.findall(r'\b(\d{5})\b', resp.text)
        if codes:
            unique_codes = list(set(codes))[:20]
            print(f"Found codes: {unique_codes}")
        
        # 保存部分内容看看
        print(f"Sample: {resp.text[:500]}")
        print()
        
    except Exception as e:
        print(f"Error: {e}")
        print()

# 尝试阿斯达克API
print("=== Trying AAStocks API ===")
try:
    aastocks_url = "https://www.aastocks.com/tc/ipo/ipoList.aspx"
    resp = requests.get(aastocks_url, headers=headers, timeout=15)
    print(f"Status: {resp.status_code}")
    print(f"Content: {resp.text[:1000]}")
except Exception as e:
    print(f"Error: {e}")
