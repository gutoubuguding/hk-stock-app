#!/usr/bin/env python3
"""Scrape HK upcoming IPO data from web sources"""
import requests
from bs4 import BeautifulSoup
import re
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

print("=" * 60)
print("Testing various HK IPO data sources")
print("=" * 60)

# Source 1: AASTOCKS upcoming IPO
print("\n[1] AASTOCKS - Upcoming IPO page")
try:
    url = 'https://www.aastocks.com/sc/stocks/market/ipo/pendingipo.aspx'
    r = requests.get(url, headers=headers, timeout=15)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Find all tables
    tables = soup.find_all('table')
    print(f'  Status: {r.status_code}, Tables: {len(tables)}')
    
    # Find IPO data rows
    rows = soup.find_all('tr')
    print(f'  Total rows: {len(rows)}')
    
    # Extract text content from first few rows
    for i, row in enumerate(rows[1:8]):
        cells = row.find_all(['td', 'th'])
        text = ' | '.join([c.get_text(strip=True)[:25] for c in cells[:7]])
        if text.strip():
            print(f'  Row {i+1}: {text}')
            
except Exception as e:
    print(f'  Error: {e}')

# Source 2: AASTOCKS - AJAX data endpoint
print("\n[2] AASTOCKS - AJAX endpoint for pending IPOs")
try:
    ajax_urls = [
        'https://www.aastocks.com/sc/stocks/market/ipo/ajax/GetIPOList.aspx',
        'https://www.aastocks.com/sc/stocks/market/ipo/GetData.aspx?type=pending',
    ]
    for ajax_url in ajax_urls:
        try:
            r = requests.get(ajax_url, headers=headers, timeout=10)
            print(f'  URL: {ajax_url[:60]}')
            print(f'  Status: {r.status_code}, Len: {len(r.text)}')
            if len(r.text) > 50:
                print(f'  Content[:500]: {r.text[:500]}')
        except:
            pass
except Exception as e:
    print(f'  Error: {e}')

# Source 3: Web search for working EastMoney API
print("\n[3] Testing EastMoney datacenter with various report names")
test_reports = [
    ('RPT_IPO_HK_CALENDAR', {'sortColumns': 'LISTING_DATE', 'sortTypes': '-1', 'filter': '(LISTING_DATE>="2026-04-01")'}),
    ('RPT_HK_IPO_CALENDAR', {'sortColumns': 'LISTING_DATE', 'sortTypes': '-1'}),
    ('RPT_IPO_HK_NEW', {'sortColumns': 'LISTING_DATE', 'sortTypes': '-1'}),
    ('RPT_HKNEW_IPO', {'sortColumns': 'LISTING_DATE', 'sortTypes': '-1'}),
]
for report, extra_params in test_reports:
    try:
        url = 'https://datacenter-web.eastmoney.com/api/data/v1/get'
        params = {
            'reportName': report,
            'pageSize': 5,
            'pageNumber': 1,
            'columns': 'ALL',
        }
        params.update(extra_params)
        r = requests.get(url, params=params, headers=headers, timeout=8)
        data = r.json()
        if data.get('success'):
            print(f'  SUCCESS! Report: {report}')
            print(f'  Data: {json.dumps(data[\"result\"][\"data\"][0], ensure_ascii=False)[:300]}')
        else:
            print(f'  Report={report}: {data.get("message", "no message")[:50]}')
    except Exception as e:
        print(f'  Report={report}: Error - {e}')

# Source 4: HKEX IPO calendar
print("\n[4] HKEX IPO Calendar")
try:
    url = 'https://www.hkex.com.hk/eng/csm/ws/MonthlyIpoData.aspx?sym=ipo&type=upcoming'
    r = requests.get(url, headers=headers, timeout=10)
    print(f'  Status: {r.status_code}, Len: {len(r.text)}')
    if len(r.text) > 100:
        print(f'  Content[:400]: {r.text[:400]}')
except Exception as e:
    print(f'  Error: {e}')
