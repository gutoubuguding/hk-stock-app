#!/usr/bin/env python3
"""Test EastMoney IPO API endpoints"""
import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Referer': 'https://data.eastmoney.com/'
}

urls = [
    # HK IPO
    'https://datacenter-web.eastmoney.com/api/data/v1/get?sortColumns=LISTING_DATE&sortTypes=-1&pageSize=5&pageNumber=1&reportName=RPT_IPO_HKAPPLY&columns=ALL',
    # A-share IPO calendar
    'https://datacenter-web.eastmoney.com/api/data/v1/get?sortColumns=EXPECT_LIST_DATE&sortTypes=-1&pageSize=5&pageNumber=1&reportName=RPT_IPO_MAIN&columns=ALL',
    # Try different filter
    'https://datacenter-web.eastmoney.com/api/data/v1/get?sortColumns=IPO_DATE&sortTypes=-1&pageSize=5&pageNumber=1&reportName=RPT_IPO_HKAPPLY_NEW&columns=ALL',
]

for url in urls:
    print(f'\n--- Testing: {url[:100]} ---')
    try:
        r = requests.get(url, headers=headers, timeout=10)
        data = r.json()
        print(f'Status: {r.status_code}')
        print(f'Response keys: {list(data.keys())}')
        if data.get('result') and data['result'].get('data'):
            first = data['result']['data'][0]
            print(f'Sample keys: {list(first.keys())}')
            print(f'Sample: {json.dumps(first, ensure_ascii=False)[:300]}')
        else:
            print(f'No data: {str(data)[:200]}')
    except Exception as e:
        print(f'Error: {e}')
