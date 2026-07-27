import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Set first_day_change = NULL where issue_price IS NULL and first_day_change = 100
# (these are clearly placeholder values, not real data)
cur.execute("""
    UPDATE stock_ipo 
    SET first_day_change = NULL, updated_at = NOW()
    WHERE listing_date >= '2025-01-01' 
    AND issue_price IS NULL 
    AND first_day_change = 100
""")
print(f"Fixed {cur.rowcount} placeholder first_day_change values")

conn.commit()

# Verify
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01' AND first_day_change = 100")
print(f"Remaining first_day_change = 100: {cur.fetchone()[0]}")