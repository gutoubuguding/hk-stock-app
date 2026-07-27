#!/usr/bin/env python3
"""更新IPO数据 - 添加即将上市的新股"""
import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432, database="hk_stock",
    user="postgres", password="pc20050218"
)
cur = conn.cursor()

# 添加即将上市的新股（模拟数据，日期设为未来）
upcoming_ipos = [
    ("02501", "Future Tech", "2026-04-15", 28.50, None, 15.5, "Technology", 2879),
    ("02502", "Green Energy", "2026-04-20", 15.80, None, 22.3, "New Energy", 1596),
    ("02503", "BioPharma", "2026-04-25", 45.00, None, 8.7, "Biotech", 4545),
    ("02504", "CloudSoft", "2026-05-06", 32.00, None, 12.1, "Software", 3232),
    ("02505", "EV Motors", "2026-05-12", 88.00, None, 5.2, "EV", 8888),
]

for item in upcoming_ipos:
    cur.execute("""
        INSERT INTO stock_ipo (stock_code, stock_name, listing_date, issue_price, 
                               allotment_rate, oversubscription_ratio, sector, entry_fee)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (stock_code) DO UPDATE SET
            stock_name = EXCLUDED.stock_name,
            listing_date = EXCLUDED.listing_date,
            issue_price = EXCLUDED.issue_price,
            sector = EXCLUDED.sector,
            entry_fee = EXCLUDED.entry_fee
    """, item)

conn.commit()

cur.execute("SELECT COUNT(*) FROM stock_ipo")
total = cur.fetchone()[0]
print(f"Total IPO records: {total}")

cur.execute("SELECT stock_code, stock_name, listing_date, issue_price, sector FROM stock_ipo ORDER BY listing_date DESC LIMIT 10")
print("\nIPO List (sorted by date):")
for row in cur.fetchall():
    print(f"  {row[0]} - {row[1]} | {row[2]} | {row[3]} | {row[4]}")

cur.close()
conn.close()
print("\nDone!")
