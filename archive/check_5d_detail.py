import psycopg2
import requests

conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check daily data for 09988 (Alibaba) for recent dates
cur.execute("""
    SELECT trade_date, close_price 
    FROM stock_kline 
    WHERE stock_code = '09988' AND period_type = 'D'
    ORDER BY trade_date DESC
    LIMIT 15
""")
print('=== 09988 最近日K数据 ===')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

# Check 5D data
cur.execute("""
    SELECT trade_date, open_price, close_price 
    FROM stock_kline 
    WHERE stock_code = '09988' AND period_type = '5D'
    ORDER BY trade_date DESC
    LIMIT 5
""")
print('\n=== 09988 5日K线数据(数据库) ===')
rows = cur.fetchall()
if rows:
    for row in rows:
        print(f'  {row[0]}: open={row[1]}, close={row[2]}')
else:
    print('  无5D数据(数据库中没有, 是实时计算的)')

# Check total daily records now
cur.execute("SELECT COUNT(*) FROM stock_kline WHERE period_type = 'D'")
print(f'\n总日K记录数: {cur.fetchone()[0]}')

cur.execute("SELECT MAX(trade_date) FROM stock_kline WHERE period_type = 'D'")
print(f'最新日K日期: {cur.fetchone()[0]}')

conn.close()

# Test the API
print('\n=== API测试 ===')
resp = requests.get('http://localhost:8080/api/stock/kline?stockCode=09988&periodType=5D&days=5', timeout=5)
data = resp.json()
for d in data:
    print(f'  {d["tradeDate"]}: open={d["openPrice"]}, close={d["closePrice"]}, high={d["highPrice"]}, low={d["lowPrice"]}')
