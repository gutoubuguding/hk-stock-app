import requests
resp = requests.get('http://localhost:8080/api/stock/kline?stockCode=09988&periodType=5D&days=5', timeout=5)
data = resp.json()
print(f'5日K线: {len(data)} 条')
for d in data:
    print(f'  {d["tradeDate"]}: open={d["openPrice"]}, close={d["closePrice"]}, high={d["highPrice"]}, low={d["lowPrice"]}')
