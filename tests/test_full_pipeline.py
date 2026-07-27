import requests, sys
sys.stdout.reconfigure(encoding='utf-8')

print('=== Testing IPO AI via Backend (full pipeline) ===')
resp = requests.get('http://localhost:8080/api/ipo/ai-analysis/06636', timeout=90)
data = resp.json()
print(f'stock: {data.get("stock_code")} {data.get("stock_name")}')
print(f'news_count: {data.get("news_count")}')
print(f'model: {data.get("model")}')

news = data.get('news', [])
if news:
    print(f'\n--- News ({len(news)} items) ---')
    for i, n in enumerate(news):
        print(f'  {i+1}. [{n.get("source")} | {n.get("date")}] {n.get("title")}')

analysis = data.get('analysis', '')
print(f'\n--- Analysis ({len(analysis)} chars) ---')
print(analysis[:1000])
