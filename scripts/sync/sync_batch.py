#!/usr/bin/env python3
"""分批同步股票K线数据"""
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

BATCH_SIZE = 50  # 每批处理数量

print("=" * 50)
print("分批同步股票K线数据")
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

synced = 0
failed = 0
start = time.time()

# 分批处理
for batch_start in range(0, total, BATCH_SIZE):
    batch = stocks[batch_start:batch_start + BATCH_SIZE]
    batch_num = batch_start // BATCH_SIZE + 1
    total_batches = (total + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"\n批次 {batch_num}/{total_batches}: {len(batch)} 只股票")
    
    # 每批创建新连接
    quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)
    
    for code, name in batch:
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
                except:
                    pass
            
            conn.commit()
            synced += 1
            
        except Exception as e:
            failed += 1
        
        time.sleep(0.3)
    
    quote_ctx.close()
    time.sleep(1)  # 批次间延迟

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
