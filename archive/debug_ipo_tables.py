#!/usr/bin/env python3
"""Debug: 打印AASTOCKS IPO详情页的关键表格"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False

from bs4 import BeautifulSoup
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9',
}

url = 'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol=00664#info'
resp = requests.get(url, headers=headers, timeout=15)
resp.encoding = 'utf-8'
soup = BeautifulSoup(resp.text, 'html.parser')

# 只打印包含招股、定价、日期的表格
tables = soup.find_all('table')
for i, table in enumerate(tables):
    rows = table.find_all('tr')
    all_text = ' '.join([td.get_text(strip=True) for td in table.find_all('td')])
    
    if any(kw in all_text for kw in ['招股日期', '定价日期', '招股截止', '暗盘', '每手股数']):
        print(f'\n=== Table {i} ({len(rows)} rows) ===')
        for row in rows[:8]:
            cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
            meaningful = [c for c in cells if c.strip()]
            if meaningful:
                print(f'  {meaningful}')