import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Try AASTOCKS company summary page for a recent IPO
url = 'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol=06636#info'
resp = requests.get(url, headers=headers, timeout=15)
resp.encoding = 'utf-8'
print(f'Status: {resp.status_code}, len: {len(resp.text)}')

soup = BeautifulSoup(resp.text, 'html.parser')

# Print all text content
text = soup.get_text(separator='\n')
lines = [l.strip() for l in text.split('\n') if l.strip()]
for line in lines[:100]:
    print(line)

print('\n\n=== Tables ===')
tables = soup.find_all('table')
print(f'Found {len(tables)} tables')
for i, table in enumerate(tables):
    rows = table.find_all('tr')
    if len(rows) > 2:
        print(f'\nTable {i}: {len(rows)} rows')
        for row in rows[:8]:
            cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
            meaningful = [c for c in cells if c]
            if meaningful:
                print(f'  {meaningful}')
