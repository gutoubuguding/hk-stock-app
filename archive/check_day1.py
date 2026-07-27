import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

cur.execute("""
    SELECT stock_code, stock_name, issue_price, listing_date, first_day_change
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01' AND first_day_change IS NOT NULL
    ORDER BY listing_date DESC
    LIMIT 20
""")
print("first_day_change 样本 (前20条):")
for row in cur.fetchall():
    print(f"  {row[0]} {row[1]} | 上市:{row[3]} | 发行价:{row[2]} | 首日涨跌:{row[4]}%")