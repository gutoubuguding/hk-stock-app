import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check 02476 K-line
cur.execute("""
    SELECT trade_date, close_price, period_type FROM stock_kline 
    WHERE stock_code = '02476' ORDER BY trade_date
""")
rows = cur.fetchall()
print("02476 K线:")
for row in rows:
    print(f"  {row[0]} close={row[1]} period={row[2]}")

# Check 00664 K-line
cur.execute("""
    SELECT trade_date, close_price, period_type FROM stock_kline 
    WHERE stock_code = '00664' ORDER BY trade_date LIMIT 10
""")
rows = cur.fetchall()
print("\n00664 K线 (前10条):")
for row in rows:
    print(f"  {row[0]} close={row[1]} period={row[2]}")