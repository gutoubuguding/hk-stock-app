import httpx
r = httpx.get('http://localhost:8080/api/ipo/comparison', timeout=10)
data = r.json()
items = data['data']

# Find stocks that have 7d/30d data
found = 0
for it in items:
    if it.get('sevenDayChange') is not None or it.get('thirtyDayChange') is not None:
        print(f"{it.get('stockCode')} {it.get('stockName')}: 7d={it.get('sevenDayChange')}, 30d={it.get('thirtyDayChange')}")
        found += 1
        if found >= 5:
            break

if found == 0:
    print("No stocks with 7d/30d in first 20 results")
    # Check if the data exists at all
    for it in items[20:40]:
        if it.get('sevenDayChange') is not None:
            print(f"{it.get('stockCode')}: 7d={it.get('sevenDayChange')}")
            break