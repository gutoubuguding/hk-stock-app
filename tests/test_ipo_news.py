import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

print('=== Testing IPO AI Analysis with News ===')
resp = requests.get(
    'http://localhost:8081/api/analyze/ipo',
    params={'stock_code': '06636', 'stock_name': '极视角'},
    timeout=60
)
data = resp.json()
print(f'stock_code: {data.get("stock_code")}')
print(f'stock_name: {data.get("stock_name")}')
print(f'news_count: {data.get("news_count")}')
print(f'model: {data.get("model")}')

news = data.get('news', [])
if news:
    print(f'\n--- Fetched News ({len(news)} items) ---')
    for i, n in enumerate(news):
        print(f'  {i+1}. [{n.get("source")} | {n.get("date")}] {n.get("title")}')

analysis = data.get('analysis', '')
print(f'\nanalysis length: {len(analysis)} chars')
print(f'\n--- Analysis Preview ---')
print(analysis[:600])
