import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

url = 'http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx?s=3&o=0&page=1'
resp = requests.get(url, headers=headers, timeout=15)
resp.encoding = 'utf-8'
soup = BeautifulSoup(resp.text, 'html.parser')

tables = soup.find_all('table')
print(f'Total tables: {len(tables)}')

# Check table 20 specifically
if len(tables) > 20:
    table = tables[20]
    rows = table.find_all('tr')
    print(f'Table 20: {len(rows)} rows')
    
    for i, row in enumerate(rows[:5]):
        cells = row.find_all(['td', 'th'])
        print(f'\nRow {i}: {len(cells)} cells')
        for j, cell in enumerate(cells):
            text = cell.get_text(strip=True)
            print(f'  Cell {j}: {repr(text[:80])}')

# Also check if the table might be at a different index
for idx in [19, 20, 21, 22]:
    if idx < len(tables):
        table = tables[idx]
        rows = table.find_all('tr')
        if len(rows) > 5:
            first_row = rows[0]
            cells = [td.get_text(strip=True) for td in first_row.find_all(['td', 'th'])]
            # Check if it has the IPO data pattern
            full_text = ' '.join(cells)
            if 'HK' in full_text or '倍数' in full_text or '中签' in full_text:
                print(f'\nTable {idx} might be the IPO data table ({len(rows)} rows)')
                for row in rows[:3]:
                    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                    print(f'  {[c[:30] for c in cells if c]}')
