import requests
from bs4 import BeautifulSoup
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Try the result announcement page
url = 'http://www.aastocks.com/sc/stocks/news/aafn/result-announcement'
try:
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    print(f'Status: {resp.status_code}, len: {len(resp.text)}')
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Get all text
    text = soup.get_text(separator='\n')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    for line in lines[:50]:
        print(line)
    
    print('\n=== Links ===')
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)
        if text and '配发' in text or '中签' in text or 'allotment' in href.lower() or 'result' in href.lower():
            print(f'{text} -> {href}')
    
    # Print tables
    print('\n=== Tables ===')
    tables = soup.find_all('table')
    print(f'Tables: {len(tables)}')
    for i, table in enumerate(tables):
        rows = table.find_all('tr')
        if len(rows) > 2:
            print(f'\nTable {i}: {len(rows)} rows')
            for row in rows[:5]:
                cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                meaningful = [c for c in cells if c]
                if meaningful:
                    print(f'  {meaningful}')
                    
except Exception as e:
    print(f'Error: {e}')
