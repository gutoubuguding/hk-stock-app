#!/usr/bin/env python3
"""Sync K-line data for IPO stocks and calculate metrics"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from futu import OpenQuoteContext, RET_OK, KLType
import psycopg2
import os
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

FUTU_HOST = os.getenv('FUTU_OPEND_HOST', 'host.docker.internal')
FUTU_PORT = int(os.getenv('FUTU_OPEND_PORT', '11111'))

print("=" * 50)
print("同步 IPO 股票 K 线数据并计算涨跌幅")
print("=" * 50)

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# Get IPO stocks that need K-line data
cur.execute("""
    SELECT stock_code, stock_name, listing_date, issue_price 
    FROM stock_ipo 
    WHERE listing_date IS NOT NULL 
    AND listing_date >= '2025-01-01'
    ORDER BY listing_date DESC
""")
ipos = cur.fetchall()
print(f"\n找到 {len(ipos)} 只需要同步的新股")

print("\n[1/2] 连接 Futu OpenD...")
quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

total_synced = 0
for i, (stock_code, stock_name, listing_date, issue_price) in enumerate(ipos, 1):
    futu_code = f"HK.{stock_code}"
    print(f"\n  [{i}/{len(ipos)}] {stock_code} {stock_name}")
    
    # Sync daily K-line
    ret, data, _ = quote_ctx.request_history_kline(futu_code, ktype=KLType.K_DAY, max_count=250)
    if ret != RET_OK:
        print(f"    K线同步失败: {data}")
        continue
    
    count = 0
    for _, row in data.iterrows():
        try:
            cur.execute('''
                INSERT INTO stock_kline (stock_code, period_type, trade_date, open_price, close_price, high_price, low_price, volume, turnover, change_percent, turnover_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (stock_code, period_type, trade_date) DO UPDATE SET
                    open_price = EXCLUDED.open_price,
                    close_price = EXCLUDED.close_price,
                    high_price = EXCLUDED.high_price,
                    low_price = EXCLUDED.low_price,
                    volume = EXCLUDED.volume,
                    turnover = EXCLUDED.turnover,
                    change_percent = EXCLUDED.change_percent,
                    turnover_rate = EXCLUDED.turnover_rate
            ''', (stock_code, 'D', row['time_key'], row['open'], row['close'],
                  row['high'], row['low'], row['volume'], row['turnover'],
                  row.get('change_rate', 0), row.get('turnover_rate', 0)))
            count += 1
        except Exception as e:
            pass
    
    conn.commit()
    total_synced += count
    print(f"    日K: {count} 条")
    
    # Calculate metrics
    if issue_price and listing_date:
        cur.execute("""
            SELECT trade_date, close_price 
            FROM stock_kline 
            WHERE stock_code = %s AND period_type = 'D'
            ORDER BY trade_date
        """, (stock_code,))
        klines = cur.fetchall()
        
        if klines:
            price_map = {str(row[0]): float(row[1]) for row in klines}
            listing_date_str = str(listing_date)
            issue_price_float = float(issue_price)
            
            # Find first trading day price
            first_day_price = None
            for date_str, price in sorted(price_map.items()):
                if date_str >= listing_date_str:
                    first_day_price = price
                    break
            
            if first_day_price:
                # First day change
                first_day_change = round((first_day_price - issue_price_float) / issue_price_float * 100, 2)
                cur.execute("UPDATE stock_ipo SET first_day_change = %s WHERE stock_code = %s", (first_day_change, stock_code))
                
                # 7-day change
                listing_dt = datetime.strptime(listing_date_str, '%Y-%m-%d')
                day7_dt = listing_dt + timedelta(days=7)
                day7_price = None
                for date_str, price in sorted(price_map.items()):
                    if date_str >= str(day7_dt.date()):
                        day7_price = price
                        break
                if day7_price:
                    change_7d = round((day7_price - issue_price_float) / issue_price_float * 100, 2)
                    cur.execute("UPDATE stock_ipo SET seven_day_change = %s WHERE stock_code = %s", (change_7d, stock_code))
                    print(f"    7天涨跌幅: {change_7d}%")
                
                # 30-day change
                day30_dt = listing_dt + timedelta(days=30)
                day30_price = None
                for date_str, price in sorted(price_map.items()):
                    if date_str >= str(day30_dt.date()):
                        day30_price = price
                        break
                if day30_price:
                    change_30d = round((day30_price - issue_price_float) / issue_price_float * 100, 2)
                    cur.execute("UPDATE stock_ipo SET thirty_day_change = %s WHERE stock_code = %s", (change_30d, stock_code))
                    print(f"    30天涨跌幅: {change_30d}%")
                
                # Current change
                latest_price = float(klines[-1][1])
                change_current = round((latest_price - issue_price_float) / issue_price_float * 100, 2)
                cur.execute("UPDATE stock_ipo SET current_change = %s, current_price = %s WHERE stock_code = %s",
                           (change_current, latest_price, stock_code))
                print(f"    现价涨跌幅: {change_current}%")
            
            conn.commit()

quote_ctx.close()

print(f"\n[2/2] 完成！")
print(f"  总计同步: {total_synced} 条 K 线数据")

# Show summary
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE seven_day_change IS NOT NULL")
print(f"  有7天涨跌幅的新股: {cur.fetchone()[0]} 只")
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE thirty_day_change IS NOT NULL")
print(f"  有30天涨跌幅的新股: {cur.fetchone()[0]} 只")
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE current_change IS NOT NULL")
print(f"  有现价涨跌幅的新股: {cur.fetchone()[0]} 只")

cur.close()
conn.close()
print("\n" + "=" * 50)
