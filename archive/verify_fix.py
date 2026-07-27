import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

cur.execute("""
    SELECT stock_code, stock_name, issue_price, listing_date, first_day_change
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01' AND first_day_change = 100
    ORDER BY listing_date DESC
    LIMIT 10
""")
print("Still showing 100%:")
for row in cur.fetchall():
    print(f"  {row[0]} {row[1]} | 发行价:{row[2]} | 上市日:{row[3]} | 涨跌:{row[4]}%")

print()
# Count by change value
cur.execute("""
    SELECT first_day_change, COUNT(*) 
    FROM stock_ipo WHERE listing_date >= '2025-01-01' AND first_day_change IS NOT NULL
    GROUP BY first_day_change ORDER BY COUNT(*) DESC LIMIT 10
""")
print("Distribution of first_day_change:")
for row in cur.fetchall():
    print(f"  {row[0]}%: {row[1]} stocks")