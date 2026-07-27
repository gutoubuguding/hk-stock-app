#!/usr/bin/env python3
"""Calculate IPO metrics: 7-day change, 30-day change, current change"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import psycopg2
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

print("=" * 50)
print("计算 IPO 涨跌幅指标")
print("=" * 50)

# Get all IPOs with listing date and issue price
cur.execute("""
    SELECT stock_code, stock_name, listing_date, issue_price 
    FROM stock_ipo 
    WHERE listing_date IS NOT NULL AND issue_price IS NOT NULL
    ORDER BY listing_date DESC
""")
ipos = cur.fetchall()
print(f"\n找到 {len(ipos)} 只有上市日期和发行价的新股")

updated_7d = 0
updated_30d = 0
updated_current = 0

for stock_code, stock_name, listing_date, issue_price in ipos:
    # Get K-line data for this stock
    cur.execute("""
        SELECT trade_date, close_price 
        FROM stock_kline 
        WHERE stock_code = %s AND period_type = 'D'
        ORDER BY trade_date
    """, (stock_code,))
    klines = cur.fetchall()
    
    if not klines:
        continue
    
    # Create date -> price map
    price_map = {str(row[0]): float(row[1]) for row in klines}
    
    # Find listing date price (first trading day)
    listing_date_str = str(listing_date)
    first_day_price = None
    for date_str, price in sorted(price_map.items()):
        if date_str >= listing_date_str:
            first_day_price = price
            break
    
    if first_day_price is None:
        continue
    
    # Calculate 7-day change
    from datetime import datetime, timedelta
    listing_dt = datetime.strptime(listing_date_str, '%Y-%m-%d')
    day7_dt = listing_dt + timedelta(days=7)
    day30_dt = listing_dt + timedelta(days=30)
    
    # Find closest price to 7 days after listing
    day7_price = None
    for date_str, price in sorted(price_map.items()):
        if date_str >= str(day7_dt.date()):
            day7_price = price
            break
    
    # Find closest price to 30 days after listing
    day30_price = None
    for date_str, price in sorted(price_map.items()):
        if date_str >= str(day30_dt.date()):
            day30_price = price
            break
    
    # Get current (latest) price
    latest_price = float(klines[-1][1]) if klines else None
    
    # Calculate changes
    issue_price_float = float(issue_price)
    
    if day7_price:
        change_7d = round((day7_price - issue_price_float) / issue_price_float * 100, 2)
        cur.execute("UPDATE stock_ipo SET seven_day_change = %s WHERE stock_code = %s", (change_7d, stock_code))
        updated_7d += 1
    
    if day30_price:
        change_30d = round((day30_price - issue_price_float) / issue_price_float * 100, 2)
        cur.execute("UPDATE stock_ipo SET thirty_day_change = %s WHERE stock_code = %s", (change_30d, stock_code))
        updated_30d += 1
    
    if latest_price:
        change_current = round((latest_price - issue_price_float) / issue_price_float * 100, 2)
        cur.execute("UPDATE stock_ipo SET current_change = %s, current_price = %s WHERE stock_code = %s", 
                   (change_current, latest_price, stock_code))
        updated_current += 1

conn.commit()

print(f"\n更新统计:")
print(f"  7天涨跌幅: {updated_7d} 条")
print(f"  30天涨跌幅: {updated_30d} 条")
print(f"  现价涨跌幅: {updated_current} 条")

# Show sample
cur.execute("""
    SELECT stock_code, stock_name, issue_price, first_day_change, seven_day_change, thirty_day_change, current_change
    FROM stock_ipo 
    WHERE seven_day_change IS NOT NULL
    ORDER BY listing_date DESC
    LIMIT 10
""")
print(f"\n示例数据 (有7天涨跌幅的新股):")
print(f"{'代码':<8} {'名称':<12} {'发行价':>8} {'首日%':>8} {'7天%':>8} {'30天%':>8} {'现价%':>8}")
print("-" * 70)
for row in cur.fetchall():
    code, name, ip, d1, d7, d30, dc = row
    print(f"{code:<8} {name:<12} {ip:>8.2f} {d1 or 0:>8.2f} {d7 or 0:>8.2f} {d30 or 0:>8.2f} {dc or 0:>8.2f}")

cur.close()
conn.close()
print("\n" + "=" * 50)
