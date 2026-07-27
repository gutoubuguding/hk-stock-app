#!/usr/bin/env python3
"""清理IPO数据，只保留真正的股票"""
import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432, database="hk_stock",
    user="postgres", password="pc20050218"
)
cur = conn.cursor()

# 统计总记录
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01'")
total = cur.fetchone()[0]
print(f"Total IPO records since 2025-01-01: {total}")

# 删除ETF和其他非股票证券
# ETF通常: 代码以8/9开头，名称包含ETF/基金/信托，或以-R/-U结尾
cur.execute("""
    DELETE FROM stock_ipo 
    WHERE listing_date >= '2025-01-01'
    AND (
        stock_name LIKE '%%ETF%%'
        OR stock_name LIKE '%%基金%%'
        OR stock_name LIKE '%%信托%%'
        OR stock_name LIKE '%%R'
        OR stock_name LIKE '%%U'
        OR stock_code LIKE '8%%'
        OR stock_code LIKE '9%%'
        OR stock_name LIKE '%%GX%%'
        OR stock_name LIKE '%%南方%%'
        OR stock_name LIKE '%%FG%%'
        OR stock_name LIKE '%%惠理%%'
    )
""")
deleted = cur.rowcount
conn.commit()
print(f"Deleted {deleted} ETF/non-stock records")

# 统计清理后
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01'")
after = cur.fetchone()[0]
print(f"After cleanup: {after} stocks")

# 按月统计
cur.execute("""
    SELECT TO_CHAR(listing_date, 'YYYY-MM') as month, COUNT(*) 
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01'
    GROUP BY TO_CHAR(listing_date, 'YYYY-MM')
    ORDER BY month
""")
print("\nMonthly distribution:")
for row in cur.fetchall():
    print(f"  {row[0]}: {row[1]} stocks")

# 显示最新的20只
cur.execute("""
    SELECT stock_code, stock_name, listing_date 
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01'
    ORDER BY listing_date DESC
    LIMIT 20
""")
print("\nLatest 20 stocks:")
for row in cur.fetchall():
    print(f"  {row[0]} - {row[1]} | {row[2]}")

cur.close()
conn.close()
print("\nDone!")
