import httpx
import json

r = httpx.get('http://localhost:8080/api/ipo/comparison', timeout=10)
data = r.json()
items = data['data']

# Find 01333 in the results
for it in items:
    if it.get('stockCode') == '01333':
        print(f"Found 01333: {json.dumps(it, ensure_ascii=False)}")
        break
    if it.get('stockCode') == '00325':
        print(f"Found 00325: {json.dumps(it, ensure_ascii=False)}")