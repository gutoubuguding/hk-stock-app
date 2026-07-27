import requests
from bs4 import BeautifulSoup
import json
import re

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json, text/html',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Try Futu/NiuNiu IPO API
print('=== Trying Futu API ===')
# Futu's IPO data API
url = 'https://www.futunn.com/api/ipo/v2/list?lang=zh-cn&market=HK&type=2'  # type=2 might be listed
try:
    resp = requests.get(url, headers=headers, timeout=15)
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, ensure_ascii=False, indent=2)[:3000])
except Exception as e:
    print(f'Error: {e}')

# Try another Futu endpoint
print('\n=== Trying Futu IPO list ===')
url2 = 'https://www.futunn.com/api/ipo/v2/list?lang=zh-cn&market=HK&type=1'  # type=1 might be upcoming
try:
    resp = requests.get(url2, headers=headers, timeout=15)
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
except Exception as e:
    print(f'Error: {e}')

# Try the niuniu website directly
print('\n=== Trying niuniu website ===')
url3 = 'https://www.futunn.com/hk/ipo'
try:
    resp = requests.get(url3, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    print(f'Status: {resp.status_code}, len={len(resp.text)}')
    soup = BeautifulSoup(resp.text, 'html.parser')
    # Look for any JSON data embedded in the page
    scripts = soup.find_all('script')
    for script in scripts:
        text = script.string
        if text and ('ipo' in text.lower() or 'winning' in text.lower() or '中签' in text):
            print(f'Found script with IPO data: {text[:500]}')
            break
except Exception as e:
    print(f'Error: {e}')

# Try gelonghui
print('\n=== Trying gelonghui API ===')
url4 = 'https://www.gelonghui.com/api/ipo/list?type=all&pageSize=30&page=1'
try:
    resp = requests.get(url4, headers=headers, timeout=15)
    print(f'Status: {resp.status_code}')
    if resp.status_code == 200:
        data = resp.json()
        print(json.dumps(data, ensure_ascii=False, indent=2)[:2000])
except Exception as e:
    print(f'Error: {e}')
