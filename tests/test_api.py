#!/usr/bin/env python3
"""测试不同的东方财富报表名"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False
import json

report_names = [
    'RPT_HK_IPOAPPLY',
    'RPT_IPO_HKAPPLY', 
    'RPTA_APP_IPO_HK',
    'RPT_HK_NEWSTOCK',
    'RPT_HK_IPO_LIST',
    'RPT_HKAPP_IPOAPPLY'
]

headers = {
    'User-Agent': 'Mozilla/5.0',
    'Referer': 'https://data.eastmoney.com/'
}

url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'

for name in report_names:
    params = {
        'sortColumns': 'LISTING_DATE',
        'sortTypes': '-1',
        'pageSize': 10,
        'pageNumber': 1,
        'reportName': name,
        'columns': 'ALL'
    }
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=10)
        data = resp.json()
        if data.get('result') and data['result'].get('data'):
            count = len(data['result']['data'])
            keys = list(data['result']['data'][0].keys())[:10]
            print(f"{name}: SUCCESS - {count} records")
            print(f"  Keys: {keys}")
        else:
            msg = data.get('message', 'no data')[:50]
            print(f"{name}: {msg}")
    except Exception as e:
        print(f"{name}: {e}")
