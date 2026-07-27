#!/usr/bin/env python3
"""精确解析Table 21的招股日期"""
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

table = soup.find_all('table')[21]  # Table 21
rows = table.find_all('tr')

print("Table 21 all rows:")
for i, row in enumerate(rows[:10]):
    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
    print(f"Row {i}: cells={cells}")
    for j, cell in enumerate(cells):
        print(f"  Cell {j}: repr={repr(cell[:100])}")

# Test the regex patterns
print("\n\nTest patterns on row 1 cells:")
row1_cells = rows[1].find_all('td')
for j, cell in enumerate(row1_cells):
    cell_text = cell.get_text(strip=True)
    cell_clean = re.sub(r'\s+', ' ', cell_text)
    print(f"Cell {j}: text='{cell_text}', clean='{cell_clean}'")
    print(f"  Match '^招股日期$': {bool(re.search(r'^招股日期$', cell_clean))}")
    
    # Check for date range
    m = re.search(r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})\s*-\s*(\d{4}[/-]\d{1,2}[/-]\d{1,2})', cell_text)
    if m:
        print(f"  Date range found: {m.group(1)} - {m.group(2)}")