#!/usr/bin/env python3
"""批量拉取港股K线数据并存入数据库"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False

import akshare as ak
import psycopg2
import time

conn = psycopg2.connect(
    host="localhost", port=5432, database="hk_stock",
    user="postgres", password="pc20050218"
)
cur = conn.cursor()

# 热门股票优先
hot_codes = ['00700', '09988', '03690', '01810', '00005', '01299', '02318', '00941', '03988', '02020',
             '01211', '09618', '06862', '02382', '09888', '00288', '01024', '09999', '06060', '02269']

cur.execute("SELECT stock_code FROM stock_info WHERE stock_code NOT IN %s ORDER BY stock_code LIMIT 180", (tuple(hot_codes),))
other_codes = [r[0] for r in cur.fetchall()]
target_codes = hot_codes + other_codes

print(f"Will fetch K-line for {len(target_codes)} stocks")

count = 0
errors = 0

for code in target_codes:
    try:
        df = ak.stock_hk_daily(symbol=code, adjust='')
        
        if df.empty:
            continue
        
        # 只保留最近120天
        df = df.tail(120)
        
        for _, row in df.iterrows():
            try:
                trade_date = str(row['date'])
                open_price = float(row['open']) if row['open'] else None
                close_price = float(row['close']) if row['close'] else None
                high_price = float(row['high']) if row['high'] else None
                low_price = float(row['low']) if row['low'] else None
                volume = int(row['volume']) if row['volume'] else 0
                turnover = float(row['amount']) if row['amount'] else 0
                
                if not open_price or not close_price:
                    continue
                
                cur.execute("""
                    INSERT INTO stock_kline (stock_code, period_type, trade_date, open_price, close_price, 
                                            high_price, low_price, volume, turnover)
                    VALUES (%s, 'D', %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stock_code, period_type, trade_date) DO UPDATE SET
                        open_price = EXCLUDED.open_price,
                        close_price = EXCLUDED.close_price,
                        high_price = EXCLUDED.high_price,
                        low_price = EXCLUDED.low_price,
                        volume = EXCLUDED.volume,
                        turnover = EXCLUDED.turnover
                """, (code, trade_date, open_price, close_price, high_price, low_price, volume, turnover))
            except Exception as e:
                conn.rollback()
                continue
        
        conn.commit()
        count += 1
        if count % 20 == 0:
            print(f"Progress: {count}/{len(target_codes)} stocks done")
        
        time.sleep(0.2)
        
    except Exception as e:
        errors += 1
        conn.rollback()
        continue

print(f"\nDone! Fetched K-line for {count} stocks, {errors} errors")

cur.execute("SELECT COUNT(*) FROM stock_kline")
total = cur.fetchone()[0]
print(f"Total K-line records: {total}")

cur.execute("SELECT trade_date, close_price FROM stock_kline WHERE stock_code='00700' ORDER BY trade_date DESC LIMIT 5")
print("\nTencent recent:")
for r in cur.fetchall():
    print(f"  {r[0]}: {r[1]}")

cur.close()
conn.close()
