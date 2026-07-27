import psycopg2
import requests

conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check daily K data stats
cur.execute("""
    SELECT stock_code, COUNT(*) as cnt 
    FROM stock_kline 
    WHERE period_type = 'D' 
    GROUP BY stock_code 
    ORDER BY cnt DESC 
    LIMIT 10
""")
print('=== 日K数据最多的股票 ===')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]} 条日K')

cur.execute("SELECT COUNT(DISTINCT stock_code) FROM stock_kline WHERE period_type = 'D'")
print(f'\n有日K数据的股票总数: {cur.fetchone()[0]}')

cur.execute("""
    SELECT MIN(trade_date), MAX(trade_date), COUNT(*) 
    FROM stock_kline 
    WHERE period_type = 'D'
""")
row = cur.fetchone()
print(f'日K数据范围: {row[0]} ~ {row[1]}, 总条数: {row[2]}')

# Check stocks with less than 5 days of data (can't form 5-day K)
cur.execute("""
    SELECT COUNT(*) FROM (
        SELECT stock_code FROM stock_kline 
        WHERE period_type = 'D'
        GROUP BY stock_code 
        HAVING COUNT(*) < 5
    ) t
""")
print(f'\n日K不足5条的股票: {cur.fetchone()[0]}')

conn.close()

# Test the 5D API for a few stocks
print('\n=== 测试5日K线API ===')
test_codes = ['09988', '01810', '00700', '03690']
for code in test_codes:
    try:
        resp = requests.get(f'http://localhost:8080/api/stock/kline?stockCode={code}&periodType=5D&days=10', timeout=5)
        import json
        data = resp.json()
        print(f'{code}: {len(data)} 条5日K线')
        if data:
            print(f'  最新: {data[-1]["tradeDate"]} 收盘={data[-1]["closePrice"]}')
    except Exception as e:
        print(f'{code}: Error - {e}')
