import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Get the AASTOCKS IPO page and look for all JavaScript to find API endpoints
url = 'http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx'
resp = requests.get(url, headers=headers, timeout=15)
resp.encoding = 'utf-8'

# Extract all JavaScript content
soup = BeautifulSoup(resp.text, 'html.parser')

# Find all script tags
for script in soup.find_all('script'):
    text = script.string or ''
    if 'ipo' in text.lower() or 'allotment' in text.lower() or '中签' in text or 'ajax' in text.lower():
        # Find URLs in this script
        urls = re.findall(r'["\']([^"\']*(?:\.aspx|\.ashx|\.php|\.json|api)[^"\']*)["\']', text)
        if urls:
            print(f'Found URLs in script:')
            for u in urls:
                print(f'  {u}')
        
        # Find function names related to IPO
        functions = re.findall(r'function\s+(\w*(?:ipo|allotment|data|load)\w*)', text, re.IGNORECASE)
        if functions:
            print(f'Found functions: {functions}')

# Check for any data in the page that might be IPO allocation
print('\n=== Looking for allocation data in page ===')
text = resp.text

# Look for percentage patterns that might be success rates
rates = re.findall(r'(\d+\.?\d*)%', text)
print(f'All percentages found: {rates[:20]}')

# Look for numeric patterns near Chinese keywords
allotment_sections = re.findall(r'(?:中签|配发|分配).{0,200}', text)
for section in allotment_sections[:5]:
    print(f'Allotment section: {section[:100]}')

# Try different AASTOCKS IPO pages
other_urls = [
    'http://www.aastocks.com/sc/stocks/market/ipo/mainpage.aspx',
    'http://www.aastocks.com/sc/stocks/market/ipo/ipo-statistics.aspx',
]
for u in other_urls:
    try:
        resp = requests.get(u, headers=headers, timeout=10)
        resp.encoding = 'utf-8'
        print(f'\n{u}: status={resp.status_code}, len={len(resp.text)}')
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('table')
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if len(rows) > 5:
                print(f'  Table {i}: {len(rows)} rows')
                for row in rows[:3]:
                    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                    meaningful = [c for c in cells if c and len(c) < 100]
                    if meaningful and len(meaningful) > 2:
                        print(f'    {meaningful}')
    except Exception as e:
        print(f'{u}: Error - {e}')
