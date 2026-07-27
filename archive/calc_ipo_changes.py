#!/usr/bin/env python3
"""计算新股的7日、30日涨跌幅"""
import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Get all IPOs with issue_price
cur.execute("""
    SELECT stock_code, stock_name, issue_price, listing_date 
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01' 
    AND issue_price IS NOT NULL 
    AND issue_price > 0
    ORDER BY listing_date
""")
ipos = cur.fetchall()
print(f"需要计算的IPO数量: {len(ipos)}")

success = 0
for code, name, issue_price, listing_date in ipos:
    try:
        # Get daily K-line data for this stock after listing date
        cur.execute("""
            SELECT close_price FROM stock_kline 
            WHERE stock_code = %s AND period_type = 'D' AND trade_date >= %s
            ORDER BY trade_date
            LIMIT 35
        """, (code, listing_date))
        rows = cur.fetchall()
        
        if len(rows) < 2:
            print(f"{code}: K线不足({len(rows)}条)")
            continue
        
        # 7-day change: close price on 7th trading day (index 7 = 8th day, index 6 = 7th day)
        seven_day_change = None
        if len(rows) >= 8:
            close_7d = float(rows[6][0])  # 7th trading day (0-indexed)
            seven_day_change = round((close_7d - float(issue_price)) / float(issue_price) * 100, 2)
        
        # 30-day change: close price on 30th trading day (index 29)
        thirty_day_change = None
        if len(rows) >= 31:
            close_30d = float(rows[29][0])
            thirty_day_change = round((close_30d - float(issue_price)) / float(issue_price) * 100, 2)
        
        # Update database
        cur.execute("""
            UPDATE stock_ipo 
            SET seven_day_change = %s, thirty_day_change = %s, updated_at = NOW()
            WHERE stock_code = %s
        """, (seven_day_change, thirty_day_change, code))
        success += 1
        
        if seven_day_change is not None or thirty_day_change is not None:
            print(f"{code} {name}: 7日={seven_day_change}%, 30日={thirty_day_change}%")
        
    except Exception as e:
        print(f"{code} {name}: 错误 - {e}")

conn.commit()
print(f"\n完成! 更新了 {success} 条记录")