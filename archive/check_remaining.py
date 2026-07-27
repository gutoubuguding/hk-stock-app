import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

cur.execute("""
    SELECT stock_code, stock_name, issue_price, first_day_change
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01' AND first_day_change = 100
""")
for row in cur.fetchall():
    print(f"  {row[0]} {row[1]}: issue={row[2]}, firstDay={row[3]}")

print()
# Count missing issue_price
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01' AND issue_price IS NULL")
print(f"Missing issue_price: {cur.fetchone()[0]}")