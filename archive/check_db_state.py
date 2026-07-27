import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check specific stocks
cur.execute("""
    SELECT stock_code, stock_name, issue_price, first_day_change, 
           seven_day_change, thirty_day_change, current_change
    FROM stock_ipo 
    WHERE stock_code IN ('02476', '00664', '00325')
""")
for row in cur.fetchall():
    print(f"{row[0]} {row[1]}: issue={row[2]}, firstDay={row[3]}, 7d={row[4]}, 30d={row[5]}, curr={row[6]}")

print()
# Check how many have issue_price but first_day_change = 100 (wrong placeholder)
cur.execute("""
    SELECT COUNT(*) FROM stock_ipo 
    WHERE listing_date >= '2025-01-01' AND first_day_change = 100
""")
print("first_day_change = 100:", cur.fetchone()[0])

# Check first_day_change = 100 that might be wrong (where we have real data)
cur.execute("""
    SELECT COUNT(*) FROM stock_ipo 
    WHERE listing_date >= '2025-01-01' AND first_day_change = 100 AND sector IS NOT NULL
""")
print("first_day_change = 100 with sector:", cur.fetchone()[0])