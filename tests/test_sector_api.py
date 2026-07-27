import httpx
import urllib.parse

# Try AI sector with query param
r = httpx.get('http://localhost:8080/api/ipo/sector', params={'sector': 'AI/软件'}, timeout=10)
print('Status:', r.status_code)
d = r.json()
print('total:', d.get('total'))
print('First 2 ipos:')
for ipo in d.get('ipos', [])[:2]:
    print(f"  {ipo['stockCode']} {ipo['stockName']}")