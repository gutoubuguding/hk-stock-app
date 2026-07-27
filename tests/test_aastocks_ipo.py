import requests
from bs4 import BeautifulSoup
import re

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

# Try the aastocks IPO listed page
url = 'http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx'
resp = requests.get(url, headers=headers, timeout=15)
resp.encoding = 'utf-8'
soup = BeautifulSoup(resp.text, 'html.parser')

# Find links with stock codes
links = soup.find_all('a', href=True)
for l in links:
    href = l['href']
    text = l.get_text(strip=True)
    if 'symbol' in href.lower() or re.search(r'\d{4,}', text):
        print(f'HREF: {href[:100]} | TEXT: {text[:50]}')
        if len([x for x in links if 'symbol' in x['href'].lower()]) > 5:
            break

# Try to parse the table structure
tables = soup.find_all('table')
print(f'\nTotal tables: {len(tables)}')

# Find a specific stock detail URL pattern
for table in tables:
    rows = table.find_all('tr')
    for row in rows:
        cells = row.find_all('td')
        for cell in cells:
            links_in_cell = cell.find_all('a', href=True)
            for link in links_in_cell:
                if 'symbol' in link['href'].lower():
                    print(f'Found: {link["href"]} -> {link.get_text(strip=True)}')
                    break
            if 'HK' in cell.get_text():
                print(f'Cell with HK: {cell.get_text(strip=True)[:200]}')