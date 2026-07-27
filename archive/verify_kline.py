import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check K-line data for 00664
cur.execute("""
    SELECT COUNT(*), period_type FROM stock_kline 
    WHERE stock_code = '00664'
    GROUP BY period_type
""")
print("00664 K线数据:")
for row in cur.fetchall():
    print(f"  period_type={row[1]}, count={row[0]}")

# Check K-line for 00325
cur.execute("""
    SELECT COUNT(*), period_type FROM stock_kline 
    WHERE stock_code = '00325'
    GROUP BY period_type
""")
print("\n00325 K线数据:")
for row in cur.fetchall():
    print(f"  period_type={row[1]}, count={row[0]}")

# Check the 7d/30d values in DB for all IPOs
cur.execute("""
    SELECT stock_code, seven_day_change, thirty_day_change 
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01' AND seven_day_change IS NOT NULL
    LIMIT 10
""")
print("\n有7日涨幅的记录:")
for row in cur.fetchall():
    print(f"  {row[0]}: 7d={row[1]}, 30d={row[2]}")