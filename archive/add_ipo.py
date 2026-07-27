#!/usr/bin/env python3
"""手动添加近期港股IPO数据"""
import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432, database="hk_stock",
    user="postgres", password="pc20050218"
)
cur = conn.cursor()

# 先添加唯一约束
try:
    cur.execute("ALTER TABLE stock_ipo ADD CONSTRAINT uk_ipo_code UNIQUE (stock_code)")
    conn.commit()
except:
    conn.rollback()

ipo_data = [
    ("09618", "JD", "2025-06-18", 226.00, 10.5, 8.2, "Internet", 22828),
    ("09999", "NetEase", "2025-06-11", 123.00, 12.3, 6.5, "Internet", 12423),
    ("09888", "Baidu", "2025-06-04", 158.00, 8.7, 12.3, "Internet", 15958),
    ("06862", "Haidilao", "2025-05-28", 17.80, 25.6, 3.2, "Catering", 1798),
    ("02015", "Li Auto", "2025-05-21", 118.00, 15.2, 5.8, "EV", 11918),
    ("09866", "NIO", "2025-05-14", 108.00, 18.3, 4.5, "EV", 10908),
    ("09901", "Koolearn", "2025-05-07", 32.80, 30.2, 2.1, "Education", 3313),
    ("09626", "Bilibili", "2025-04-30", 708.00, 5.6, 25.3, "Internet", 71508),
    ("02382", "Sunny Optical", "2025-04-23", 85.50, 20.5, 4.8, "Optics", 8636),
    ("09961", "Trip.com", "2025-04-16", 198.00, 12.8, 7.5, "Travel", 19998),
]

for item in ipo_data:
    cur.execute("""
        INSERT INTO stock_ipo (stock_code, stock_name, listing_date, issue_price, 
                               allotment_rate, oversubscription_ratio, sector, entry_fee)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (stock_code) DO UPDATE SET
            stock_name = EXCLUDED.stock_name,
            listing_date = EXCLUDED.listing_date,
            issue_price = EXCLUDED.issue_price,
            allotment_rate = EXCLUDED.allotment_rate,
            oversubscription_ratio = EXCLUDED.oversubscription_ratio,
            sector = EXCLUDED.sector,
            entry_fee = EXCLUDED.entry_fee
    """, item)

conn.commit()

cur.execute("SELECT COUNT(*) FROM stock_ipo")
print(f"Total IPO records: {cur.fetchone()[0]}")

cur.execute("SELECT stock_code, stock_name, listing_date, issue_price FROM stock_ipo ORDER BY listing_date DESC LIMIT 5")
print("\nRecent IPOs:")
for row in cur.fetchall():
    print(f"  {row[0]} - {row[1]} | {row[2]} | {row[3]}")

cur.close()
conn.close()
print("Done!")
