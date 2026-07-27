#!/usr/bin/env python3
"""Complete data sync - stocks, IPO, K-line (daily/5D/monthly/yearly)"""
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

# 主要股票列表 (蓝筹股 + 热门股)
MAIN_STOCKS = [
    'HK.00700', 'HK.09988', 'HK.03690', 'HK.01810', 'HK.09618',
    'HK.02318', 'HK.00388', 'HK.01299', 'HK.02020', 'HK.01024',
    'HK.00005', 'HK.00011', 'HK.00016', 'HK.00027', 'HK.00066',
    'HK.00175', 'HK.00241', 'HK.00267', 'HK.00288', 'HK.00386',
    'HK.00669', 'HK.00688', 'HK.00762', 'HK.00823', 'HK.00857',
    'HK.00883', 'HK.00939', 'HK.00941', 'HK.00960', 'HK.01038',
    'HK.01044', 'HK.01088', 'HK.01093', 'HK.01109', 'HK.01113',
    'HK.01177', 'HK.01211', 'HK.01378', 'HK.01398', 'HK.01816',
    'HK.01876', 'HK.01928', 'HK.01929', 'HK.01997', 'HK.02007',
    'HK.02013', 'HK.02018', 'HK.02020', 'HK.02269', 'HK.02282',
    'HK.02313', 'HK.02319', 'HK.02328', 'HK.02382', 'HK.02388',
    'HK.02628', 'HK.02688', 'HK.03323', 'HK.03333', 'HK.03692',
    'HK.03968', 'HK.03988', 'HK.06030', 'HK.06060', 'HK.06862',
    'HK.09626', 'HK.09633', 'HK.09698', 'HK.09868', 'HK.09888',
    'HK.09961', 'HK.09999',
]

def sync_kline(quote_ctx, cur, stock_code, kl_type, period_type, max_count):
    """Sync K-line data for a stock"""
    ret, data, _ = quote_ctx.request_history_kline(stock_code, ktype=kl_type, max_count=max_count)
    if ret != RET_OK:
        return 0
    
    count = 0
    code = stock_code.replace('HK.', '')
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
            ''', (code, period_type, row['time_key'], row['open'], row['close'], 
                  row['high'], row['low'], row['volume'], row['turnover'], 
                  row.get('change_rate', 0), row.get('turnover_rate', 0)))
            count += 1
        except Exception as e:
            pass
    return count

print("=" * 50)
print("港股数据完整同步")
print("=" * 50)

print("\n[1/3] 连接 Futu OpenD...")
quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# K-line sync config
KLINE_CONFIG = [
    (KLType.K_DAY, 'D', 250, '日K'),
    (KLType.K_WEEK, 'W', 52, '周K'),
    (KLType.K_MON, 'K_MON', 24, '月K'),
]

total_synced = 0
stock_count = len(MAIN_STOCKS)

print(f"\n[2/3] 同步 {stock_count} 只股票的 K 线数据...")

for i, code in enumerate(MAIN_STOCKS, 1):
    stock_code = code.replace('HK.', '')
    print(f"\n  [{i}/{stock_count}] {code}")
    
    for kl_type, period_type, max_count, name in KLINE_CONFIG:
        count = sync_kline(quote_ctx, cur, code, kl_type, period_type, max_count)
        total_synced += count
        print(f"    {name}: {count} 条")
    
    conn.commit()

quote_ctx.close()

print(f"\n[3/3] 同步完成！")
print(f"  总计同步: {total_synced} 条 K 线数据")

# Show summary
cur.execute("SELECT period_type, COUNT(*) FROM stock_kline GROUP BY period_type ORDER BY period_type")
print(f"\n  数据库统计:")
for row in cur.fetchall():
    print(f"    {row[0]}: {row[1]} 条")

cur.execute("SELECT MIN(trade_date), MAX(trade_date) FROM stock_kline WHERE period_type = 'D'")
row = cur.fetchone()
print(f"\n  日K日期范围: {row[0]} ~ {row[1]}")

cur.close()
conn.close()
print("\n" + "=" * 50)
