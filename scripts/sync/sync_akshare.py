#!/usr/bin/env python3
"""使用AKShare同步剩余股票K线数据"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import akshare as ak
import psycopg2
import os
from datetime import datetime, timedelta
import time

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

print("=" * 50)
print("使用AKShare同步K线数据")
print("=" * 50)

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# 获取没有K线数据的股票
cur.execute("""
    SELECT s.stock_code, s.stock_name
    FROM stock_info s
    LEFT JOIN (SELECT DISTINCT stock_code FROM stock_kline WHERE period_type = 'D') k 
        ON s.stock_code = k.stock_code
    WHERE k.stock_code IS NULL
    ORDER BY s.stock_code
""")
stocks = cur.fetchall()
total = len(stocks)
print(f"需要同步: {total} 只股票")

if total == 0:
    print("所有股票已有K线数据！")
    cur.close()
    conn.close()
    sys.exit(0)

synced = 0
failed = 0
start = time.time()

for i, (code, name) in enumerate(stocks, 1):
    try:
        # 使用AKShare获取K线数据
        try:
            df = ak.stock_hk_daily(symbol=code, adjust='')
        except KeyError:
            # 某些股票没有数据，跳过
            failed += 1
            continue
        
        if df is None or df.empty:
            failed += 1
            continue
        
        # 只保留最近250天的数据
        df = df.tail(250)
        
        count = 0
        for _, row in df.iterrows():
            try:
                # 计算涨跌幅
                change_pct = 0
                if count > 0:
                    prev_close = float(df.iloc[count-1]['close'])
                    if prev_close > 0:
                        change_pct = (float(row['close']) - prev_close) / prev_close * 100
                
                cur.execute('''
                    INSERT INTO stock_kline (stock_code, period_type, trade_date, open_price, close_price, high_price, low_price, volume, turnover, change_percent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stock_code, period_type, trade_date) DO UPDATE SET
                        open_price = EXCLUDED.open_price, close_price = EXCLUDED.close_price,
                        high_price = EXCLUDED.high_price, low_price = EXCLUDED.low_price,
                        volume = EXCLUDED.volume, turnover = EXCLUDED.turnover,
                        change_percent = EXCLUDED.change_percent
                ''', (code, 'D', row['date'], float(row['open']), float(row['close']), 
                      float(row['high']), float(row['low']), int(row['volume']), 
                      float(row['amount']), change_pct))
                count += 1
            except Exception as e:
                pass
        
        conn.commit()
        synced += 1
        
        if i % 50 == 0:
            elapsed = time.time() - start
            rate = i / elapsed * 60
            print(f"进度: {i}/{total} | 成功: {synced} | 失败: {failed} | 速度: {rate:.0f}只/分钟")
        
    except Exception as e:
        failed += 1
        if i <= 10:
            print(f"  {code} 失败: {e}")
    
    time.sleep(0.5)  # 避免请求过快

cur.execute("SELECT COUNT(DISTINCT stock_code) FROM stock_kline WHERE period_type = 'D'")
final_count = cur.fetchone()[0]
cur.close()
conn.close()

elapsed = time.time() - start
print(f"\n{'='*50}")
print(f"完成！耗时: {elapsed/60:.1f}分钟")
print(f"成功: {synced} | 失败: {failed}")
print(f"有K线的股票总数: {final_count}")
print(f"{'='*50}")
