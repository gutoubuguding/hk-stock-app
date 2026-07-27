import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Check one specific IPO detail page more carefully
code = '06636'
url = f'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol={code}'
resp = requests.get(url, headers=headers, timeout=15)
resp.encoding = 'utf-8'
soup = BeautifulSoup(resp.text, 'html.parser')

# Print ALL tables with their index and content
tables = soup.find_all('table')
print(f'Found {len(tables)} tables total\n')

for i, table in enumerate(tables):
    rows = table.find_all('tr')
    # Only print tables with meaningful content
    all_cells = []
    for row in rows:
        cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
        meaningful = [c for c in cells if len(c) > 0]
        all_cells.extend(meaningful)
    
    # Skip empty tables and navigation tables
    if len(all_cells) < 3:
        continue
    
    # Skip tables that are just navigation
    if any('首页' in c or '登录' in c for c in all_cells):
        continue
    
    print(f'=== Table {i}: {len(rows)} rows ===')
    for j, row in enumerate(rows):
        cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
        meaningful = [c for c in cells if len(c) > 0]
        if meaningful:
            print(f'  Row {j}: {meaningful}')
    print()
