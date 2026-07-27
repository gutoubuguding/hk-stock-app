import psycopg2
conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check latest dates
cur.execute("""
    SELECT trade_date, COUNT(*) as cnt
    FROM stock_kline 
    WHERE period_type = 'D' AND trade_date >= '2026-03-25'
    GROUP BY trade_date
    ORDER BY trade_date
""")
print('=== 最近每日K线记录数 ===')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]} 条')

# Check 09988 specifically
cur.execute("""
    SELECT trade_date, close_price 
    FROM stock_kline 
    WHERE stock_code = '09988' AND period_type = 'D'
    ORDER BY trade_date DESC
    LIMIT 5
""")
print('\n=== 09988 最近日K ===')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

conn.close()
