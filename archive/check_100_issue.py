import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check all stocks where first_day_change = 100
cur.execute("""
    SELECT stock_code, stock_name, issue_price, listing_date, first_day_change
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01' AND first_day_change = 100
    ORDER BY listing_date
""")
rows = cur.fetchall()
print(f"Stocks with first_day_change = 100 ({len(rows)}):")
for row in rows:
    code, name, issue_price, listing_date, fdc = row
    print(f"  {code} {name}: issue={issue_price}, listing={listing_date}, firstDay={fdc}")

print()
# Check issue_price NULL count
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01' AND issue_price IS NULL")
print(f"IPO with NULL issue_price: {cur.fetchone()[0]}")