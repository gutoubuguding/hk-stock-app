#!/usr/bin/env python3
import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute("SELECT COUNT(*), COUNT(allotment_rate) FROM stock_ipo WHERE listing_date >= '2025-01-01'")
row = cur.fetchone()
print(f"Total: {row[0]}, Has allotment_rate: {row[1]}")

cur.execute("SELECT stock_code, stock_name, allotment_rate FROM stock_ipo WHERE listing_date >= '2025-01-01' AND allotment_rate IS NOT NULL LIMIT 5")
rows = cur.fetchall()
print("\nSample with allotment_rate:")
for r in rows:
    print(f"  {r[0]} {r[1]}: {r[2]}%")

cur.close()
conn.close()
