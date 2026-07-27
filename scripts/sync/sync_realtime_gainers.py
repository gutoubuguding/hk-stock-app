#!/usr/bin/env python3
"""获取实时涨幅榜数据"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from futu import OpenQuoteContext, RET_OK
import psycopg2
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

FUTU_HOST = os.getenv('FUTU_OPEND_HOST', 'host.docker.internal')
FUTU_PORT = int(os.getenv('FUTU_OPEND_PORT', '11111'))

print("获取实时涨幅榜数据...")

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# 获取有K线数据的股票
cur.execute("""
    SELECT DISTINCT stock_code 
    FROM stock_kline 
    WHERE period_type = 'D'
    ORDER BY stock_code
""")
stocks = [row[0] for row in cur.fetchall()]
print(f"需要检查: {len(stocks)} 只股票")

quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

# 分批获取实时行情
BATCH_SIZE = 100
gainers = []

for i in range(0, len(stocks), BATCH_SIZE):
    batch = stocks[i:i+BATCH_SIZE]
    codes = [f"HK.{s}" for s in batch]
    
    ret, data = quote_ctx.get_market_snapshot(codes)
    if ret == RET_OK:
        for _, row in data.iterrows():
            code = row['code'].replace('HK.', '')
            # 计算涨跌幅: (最新价 - 昨收) / 昨收 * 100
            last_price = float(row.get('last_price', 0)) if row.get('last_price') and str(row['last_price']) != 'N/A' else 0
            prev_close = float(row.get('prev_close_price', 0)) if row.get('prev_close_price') and str(row['prev_close_price']) != 'N/A' else 0
            
            if prev_close > 0 and last_price > 0:
                change_pct = (last_price - prev_close) / prev_close * 100
                gainers.append((code, change_pct, last_price))

quote_ctx.close()

# 按涨幅排序
gainers.sort(key=lambda x: x[1], reverse=True)

# 更新数据库中的change_percent
updated = 0
for code, change_pct, _ in gainers[:50]:
    cur.execute("""
        UPDATE stock_kline 
        SET change_percent = %s 
        WHERE stock_code = %s 
          AND period_type = 'D' 
          AND trade_date = (SELECT MAX(trade_date) FROM stock_kline WHERE period_type = 'D' AND stock_code = %s)
    """, (round(change_pct, 2), code, code))
    updated += cur.rowcount

conn.commit()
cur.close()
conn.close()

print(f"更新了 {updated} 条记录")
print(f"\n涨幅榜 TOP 10:")
for code, pct, price in gainers[:10]:
    print(f"  {code}: {pct:.2f}% (现价: {price})")
