import requests
import json

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/javascript, */*',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx',
    'X-Requested-With': 'XMLHttpRequest',
}

# Try various AASTOCKS API endpoints
urls = [
    'http://www.aastocks.com/sc/stocks/market/ipo/ajax/GetIPOList.aspx',
    'http://www.aastocks.com/sc/stocks/market/ipo/ajax/GetAllotmentResult.aspx',
    'http://www.aastocks.com/tc/stocks/market/ipo/GetIPOInfo.aspx',
    'http://www.aastocks.com/api/ipo/list',
]

for url in urls:
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f'{url}: status={resp.status_code}, len={len(resp.text)}')
        if resp.status_code == 200 and len(resp.text) > 100:
            try:
                data = resp.json()
                print(f'  JSON: {json.dumps(data, ensure_ascii=False)[:500]}')
            except:
                print(f'  Text: {resp.text[:300]}')
    except Exception as e:
        print(f'{url}: Error - {e}')

# Try AASTOCKS JSONP endpoint pattern
print('\n=== Trying AASTOCKS internal APIs ===')
api_urls = [
    'http://www.aastocks.com/sc/stocks/market/ipo/ajax/GetData.aspx?type=listed',
    'http://www.aastocks.com/sc/ipo/GetData.aspx',
    'http://www.aastocks.com/data/ipo/listed',
]
for url in api_urls:
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        print(f'{url}: status={resp.status_code}, len={len(resp.text)}')
        if resp.status_code == 200 and len(resp.text) > 100:
            print(f'  Content: {resp.text[:500]}')
    except Exception as e:
        print(f'{url}: Error - {e}')

# Try to find the API by checking the page source more carefully
print('\n=== Checking page source for API endpoints ===')
resp = requests.get('http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx', headers={
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
}, timeout=15)
resp.encoding = 'utf-8'

import re
# Find all URLs in scripts
scripts = re.findall(r'src="([^"]*)"', resp.text)
api_scripts = [s for s in scripts if 'api' in s.lower() or 'ipo' in s.lower() or 'ajax' in s.lower()]
print(f'Script URLs with api/ipo/ajax: {api_scripts}')

# Find fetch/ajax calls
fetch_calls = re.findall(r'(?:fetch|ajax|get|post)\s*\(["\']([^"\']+)["\']', resp.text, re.IGNORECASE)
print(f'Fetch/AJAX calls: {fetch_calls[:10]}')

# Find API endpoint patterns
api_patterns = re.findall(r'["\']([^"\']*(?:api|ajax|json|ipo)[^"\']*)["\']', resp.text, re.IGNORECASE)
api_patterns = [p for p in api_patterns if len(p) > 5 and len(p) < 200]
print(f'API patterns: {api_patterns[:20]}')
