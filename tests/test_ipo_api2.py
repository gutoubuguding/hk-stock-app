#!/usr/bin/env python3
"""Test various HK IPO data sources"""
import requests
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

# Test 1: EastMoney IPO calendar page (web scraping)
print("=== Test: EastMoney HK IPO Calendar ===")
try:
    r = requests.get('https://data.eastmoney.com/hk/ipo.html', headers=headers, timeout=10)
    print(f'Status: {r.status_code}, Len: {len(r.text)}')
    # Look for API URLs in the page
    api_urls = re.findall(r'["\']([^"\']*ipo[^"\']*api[^"\']*)["\']', r.text, re.IGNORECASE)
    if api_urls:
        print(f'Found API URLs: {api_urls[:5]}')
    # Try to find data in the page
    ipo_data = re.findall(r'["\']code["\']\s*:\s*["\'](\w+)["\']', r.text)
    print(f'Found codes: {ipo_data[:5]}')
except Exception as e:
    print(f'Error: {e}')

# Test 2: EastMoney's actual API for HK IPO calendar
print("\n=== Test: EastMoney HK IPO API (alternate) ===")
try:
    url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
    params = {
        'sortColumns': 'APPLY_DATE',
        'sortTypes': '-1',
        'pageSize': 10,
        'pageNumber': 1,
        'reportName': 'RPT_HK_IPO_LIST',
        'columns': 'ALL',
    }
    r = requests.get(url, params=params, headers=headers, timeout=10)
    data = r.json()
    print(f'Response: {json.dumps(data, ensure_ascii=False)[:300]}')
except Exception as e:
    print(f'Error: {e}')

# Test 3: Try a different EastMoney endpoint format
print("\n=== Test: EastMoney IPO List v2 ===")
try:
    url = 'https://datacenter.eastmoney.com/securities/api/data/v1/get'
    params = {
        'reportName': 'RPT_IPO_HK_DETAIL',
        'columns': 'ALL',
        'pageNumber': 1,
        'pageSize': 5,
        'sortTypes': -1,
        'sortColumns': 'LISTING_DATE',
    }
    r = requests.get(url, params=params, headers=headers, timeout=10)
    data = r.json()
    print(f'Status: {r.status_code}')
    print(f'Response: {json.dumps(data, ensure_ascii=False)[:300]}')
except Exception as e:
    print(f'Error: {e}')

# Test 4: AASTOCKS IPO
print("\n=== Test: AASTOCKS IPO ===")
try:
    url = 'https://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx'
    r = requests.get(url, headers=headers, timeout=10)
    print(f'Status: {r.status_code}, Len: {len(r.text)}')
    # Extract IPO data
    codes = re.findall(r'(\d{5})\s*</a>', r.text)
    names = re.findall(r'<a[^>]+>([^<]+)</a>[^<]*(?:\d{5})', r.text)
    print(f'Found codes: {codes[:5]}')
except Exception as e:
    print(f'Error: {e}')

# Test 5: 经济通 IPO calendar
print("\n=== Test: ETNet HK IPO ===")
try:
    url = 'https://www.etnet.com.hk/www/tc/stocks/ipo_calendar.php'
    r = requests.get(url, headers=headers, timeout=10)
    print(f'Status: {r.status_code}, Len: {len(r.text)}')
except Exception as e:
    print(f'Error: {e}')
