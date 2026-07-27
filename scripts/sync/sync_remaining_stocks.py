#!/usr/bin/env python3
"""同步剩余股票K线数据 - 最终版"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from futu import OpenQuoteContext, RET_OK, KLType
import psycopg2
import os
import time

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
print("同步剩余股票K线数据")
print("=" * 50)

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

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

# 连接 Futu OpenD
print(f"连接 Futu OpenD: {FUTU_HOST}:{FUTU_PORT}")
quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

synced = 0
failed = 0
start = time.time()

for i, (code, name) in enumerate(stocks, 1):
    futu_code = f"HK.{code}"
    try:
        ret, data, _ = quote_ctx.request_history_kline(futu_code, ktype=KLType.K_DAY, max_count=250)
        if ret != RET_OK or data is None or data.empty:
            failed += 1
            continue
        
        count = 0
        for _, row in data.iterrows():
            try:
                cur.execute('''
                    INSERT INTO stock_kline (stock_code, period_type, trade_date, open_price, close_price, high_price, low_price, volume, turnover, change_percent, turnover_rate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stock_code, period_type, trade_date) DO UPDATE SET
                        open_price = EXCLUDED.open_price, close_price = EXCLUDED.close_price,
                        high_price = EXCLUDED.high_price, low_price = EXCLUDED.low_price,
                        volume = EXCLUDED.volume, turnover = EXCLUDED.turnover,
                        change_percent = EXCLUDED.change_percent, turnover_rate = EXCLUDED.turnover_rate
                ''', (code, 'D', row['time_key'], row['open'], row['close'], row['high'], row['low'], 
                      row['volume'], row['turnover'], row.get('change_rate', 0), row.get('turnover_rate', 0)))
                count += 1
            except Exception as e:
                pass
        
        conn.commit()
        synced += 1
        
        if i % 100 == 0:
            elapsed = time.time() - start
            rate = i / elapsed * 60
            print(f"进度: {i}/{total} | 成功: {synced} | 失败: {failed} | 速度: {rate:.0f}只/分钟")
        
    except Exception as e:
        failed += 1
        if i <= 10:
            print(f"  {code} 失败: {e}")
    
    time.sleep(0.5)  # 增加延迟

quote_ctx.close()

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
