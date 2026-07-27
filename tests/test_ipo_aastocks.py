#!/usr/bin/env python3
"""Scrape HK IPO data from AASTOCKS"""
import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# AASTOCKS listed IPO page
print("=== AASTOCKS Listed IPO ===")
url = 'https://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx'
try:
    r = requests.get(url, headers=headers, timeout=15)
    r.encoding = 'utf-8'
    soup = BeautifulSoup(r.text, 'html.parser')
    
    # Find table rows
    rows = soup.select('table tr')
    print(f'Found {len(rows)} table rows')
    
    for row in rows[:5]:
        cells = row.find_all('td')
        if cells:
            print([c.get_text(strip=True)[:20] for c in cells[:6]])
    
    # Also look for specific patterns
    links = soup.find_all('a', href=re.compile(r'ipo|stock'))
    print(f'\nFound {len(links)} IPO-related links')
    for link in links[:10]:
        print(f'  {link.get("href", "")} - {link.get_text(strip=True)[:30]}')
        
except Exception as e:
    print(f'Error: {e}')

# Try the AJAX endpoint that AASTOCKS uses
print("\n=== AASTOCKS AJAX API ===")
ajax_urls = [
    'https://www.aastocks.com/sc/stocks/market/ipo/ajax/GetIPOList.aspx',
    'https://www.aastocks.com/sc/stocks/market/ipo/ajax/GetListedIPO.aspx',
    'http://www.aastocks.com/sc/stocks/market/ipo/ajax/GetData.aspx?type=listed',
]
for ajax_url in ajax_urls:
    try:
        r = requests.get(ajax_url, headers=headers, timeout=10)
        print(f'\nURL: {ajax_url}')
        print(f'Status: {r.status_code}, Len: {len(r.text)}')
        print(f'Content[:300]: {r.text[:300]}')
    except Exception as e:
        print(f'Error: {e}')
