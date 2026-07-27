import requests
from bs4 import BeautifulSoup
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Try AASTOCKS allocation result page
url = 'http://www.aastocks.com/sc/stocks/market/ipo/iporesult.aspx'
try:
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    print(f'Status: {resp.status_code}, len: {len(resp.text)}')
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    tables = soup.find_all('table')
    print(f'Tables: {len(tables)}')
    
    for i, table in enumerate(tables):
        rows = table.find_all('tr')
        if len(rows) > 3:
            print(f'\n=== Table {i}: {len(rows)} rows ===')
            for j, row in enumerate(rows[:10]):
                cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                meaningful = [c for c in cells if c and len(c) < 100]
                if meaningful:
                    print(f'  Row {j}: {meaningful}')
except Exception as e:
    print(f'Error: {e}')

# Also try listing page with pagination
print('\n\n=== Trying IPO allocation listing ===')
url2 = 'http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx'
try:
    resp = requests.get(url2, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Look for any hidden data or API calls
    for script in soup.find_all('script'):
        text = script.string or ''
        if 'allotment' in text.lower() or 'allocation' in text.lower() or '中签' in text or 'iporesult' in text.lower():
            print(f'Found relevant script: {text[:500]}')
    
    # Look for links to IPO result pages
    for a in soup.find_all('a', href=True):
        href = a['href']
        if 'result' in href.lower() or 'allocation' in href.lower() or 'allotment' in href.lower():
            print(f'Found link: {a.get_text(strip=True)} -> {href}')
            
except Exception as e:
    print(f'Error: {e}')
