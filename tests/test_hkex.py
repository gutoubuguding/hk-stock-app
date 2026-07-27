#!/usr/bin/env python3
"""尝试从港交所获取IPO数据"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/html'
}

# 尝试港交所不同URL
urls = [
    'https://www.hkex.com.hk/Services/Trading/Securities/Securities-Lists/Newly-Listed-Securities',
    'https://www.hkex.com.hk/Services/Trading/Securities/Securities-Lists/Securities-Lists',
    'https://www1.hkexnews.hk/ncms/json/eds/lci_main.json',
    'https://www.hkex.com.hk/chi/invest/company/profile_c.htm',
    'https://www.hkex.com.hk/investor-corner/ipo/ipo-information',
]

for url in urls:
    try:
        print(f'Trying: {url[:70]}...')
        resp = requests.get(url, headers=headers, timeout=10)
        print(f'  Status: {resp.status_code}')
        if resp.status_code == 200:
            ctype = resp.headers.get('content-type', '')
            print(f'  Content-Type: {ctype}')
            print(f'  Length: {len(resp.text)}')
            print(f'  Sample: {resp.text[:200]}')
        print()
    except Exception as e:
        print(f'  Error: {e}')
        print()
