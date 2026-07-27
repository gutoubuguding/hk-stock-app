#!/usr/bin/env python3
"""批量同步所有港股K线数据 - 后台运行版本"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from futu import OpenQuoteContext, RET_OK, KLType
import psycopg2
import os
import time
from datetime import datetime

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

FUTU_HOST = os.getenv('FUTU_OPEND_HOST', 'host.docker.internal')
FUTU_PORT = int(os.getenv('FUTU_OPEND_PORT', '11111'))

# 批量同步配置
BATCH_SIZE = 50  # 每批处理股票数
DELAY_BETWEEN_STOCKS = 0.5  # 每只股票间隔秒数
DELAY_BETWEEN_BATCHES = 5  # 每批间隔秒数

print("=" * 60)
print("港股K线数据批量同步")
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

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
total_stocks = len(stocks)
print(f"\n需要同步K线的股票: {total_stocks} 只")

if total_stocks == 0:
    print("所有股票已有K线数据！")
    cur.close()
    conn.close()
    sys.exit(0)

# 连接Futu OpenD
print("\n连接 Futu OpenD...")
quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

total_synced = 0
failed_count = 0
start_time = time.time()

# 分批处理
for batch_start in range(0, total_stocks, BATCH_SIZE):
    batch_end = min(batch_start + BATCH_SIZE, total_stocks)
    batch = stocks[batch_start:batch_end]
    batch_num = batch_start // BATCH_SIZE + 1
    total_batches = (total_stocks + BATCH_SIZE - 1) // BATCH_SIZE
    
    print(f"\n{'='*40}")
    print(f"批次 {batch_num}/{total_batches}: 处理 {len(batch)} 只股票")
    print(f"{'='*40}")
    
    for i, (stock_code, stock_name) in enumerate(batch, 1):
        global_idx = batch_start + i
        futu_code = f"HK.{stock_code}"
        
        try:
            # 获取日K数据
            ret, data, _ = quote_ctx.request_history_kline(futu_code, ktype=KLType.K_DAY, max_count=250)
            
            if ret != RET_OK:
                print(f"  [{global_idx}/{total_stocks}] {stock_code} {stock_name}: 失败 - {data}")
                failed_count += 1
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
            
            if global_idx % 10 == 0:  # 每10只股票打印一次进度
                elapsed = time.time() - start_time
                rate = global_idx / elapsed * 60 if elapsed > 0 else 0
                print(f"  [{global_idx}/{total_stocks}] {stock_code}: {count}条 | 速度: {rate:.0f}只/分钟 | 失败: {failed_count}")
            
        except Exception as e:
            print(f"  [{global_idx}/{total_stocks}] {stock_code}: 异常 - {e}")
            failed_count += 1
        
        # 延迟避免限流
        time.sleep(DELAY_BETWEEN_STOCKS)
    
    # 批次间延迟
    if batch_end < total_stocks:
        print(f"\n批次完成，等待 {DELAY_BETWEEN_BATCHES} 秒...")
        time.sleep(DELAY_BETWEEN_BATCHES)

quote_ctx.close()

# 最终统计
elapsed = time.time() - start_time
cur.execute("SELECT COUNT(DISTINCT stock_code) FROM stock_kline WHERE period_type = 'D'")
total_with_kline = cur.fetchone()[0]

cur.execute("SELECT COUNT(*) FROM stock_kline WHERE period_type = 'D'")
total_kline_records = cur.fetchone()[0]

cur.close()
conn.close()

print(f"\n{'='*60}")
print(f"同步完成！")
print(f"  总耗时: {elapsed/60:.1f} 分钟")
print(f"  同步股票: {total_stocks - failed_count} 只")
print(f"  失败: {failed_count} 只")
print(f"  新增K线: {total_synced} 条")
print(f"  有K线的股票总数: {total_with_kline} 只")
print(f"  K线记录总数: {total_kline_records} 条")
print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"{'='*60}")
