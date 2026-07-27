import httpx
r = httpx.get('http://localhost:8080/api/ipo/comparison', timeout=10)
data = r.json()
items = data['data'][:10]
for it in items:
    print(f"{it.get('stockCode')} {it.get('stockName')}: issue={it.get('issuePrice')}, firstDay={it.get('firstDayChange')}, 7d={it.get('sevenDayChange')}, 30d={it.get('thirtyDayChange')}, curr={it.get('currentChange')}")