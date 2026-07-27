#!/usr/bin/env python3
import psycopg2
from datetime import date

conn = psycopg2.connect(host='localhost', port=5432, dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

today = date.today()
print(f"Today: {today}")

# Get all IPOs from 2026 onwards
cur.execute("SELECT stock_code, stock_name, listing_date, issue_price FROM stock_ipo WHERE listing_date >= '2026-01-01' ORDER BY listing_date DESC LIMIT 30")
rows = cur.fetchall()

past = [r for r in rows if r[2] <= today]
future = [r for r in rows if r[2] > today]

print(f"Total: {len(rows)}, Past (listed): {len(past)}, Future (upcoming): {len(future)}")
print(f"\nFuture (upcoming) IPOs:")
for r in future:
    print(f"  {r[0]} | {r[1]} | {r[2]} | issue_price={r[3]}")

print(f"\nRecent past IPOs (last 15):")
for r in past[-15:]:
    print(f"  {r[0]} | {r[1]} | {r[2]} | issue_price={r[3]}")

cur.close()
conn.close()
