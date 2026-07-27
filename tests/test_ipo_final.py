import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

print('=== Testing IPO AI Analysis ===')
resp = requests.get('http://localhost:8080/api/ipo/ai-analysis/06636', timeout=60)
data = resp.json()
print(f'stock_code: {data.get("stock_code")}')
print(f'stock_name: {data.get("stock_name")}')
print(f'model: {data.get("model")}')

analysis = data.get('analysis', '')
print(f'\nanalysis length: {len(analysis)} chars')
print(f'\n--- Analysis Preview ---')
print(analysis[:800])
