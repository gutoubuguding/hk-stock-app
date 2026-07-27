#!/usr/bin/env python3
"""通过Futu获取IPO股票的发行价和首日表现"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import psycopg2
from futu import *
import time

print('Connecting to Futu OpenD...')
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
print('Connected!')

conn = psycopg2.connect(
    host="localhost", port=5432, database="hk_stock",
    user="postgres", password="pc20050218"
)
cur = conn.cursor()

# 获取IPO股票列表
cur.execute("SELECT stock_code, listing_date FROM stock_ipo WHERE listing_date >= '2025-01-01' ORDER BY listing_date")
stocks = cur.fetchall()
print(f'Processing {len(stocks)} stocks...')

codes = [f'HK.{s[0]}' for s in stocks]

# 批量获取股票快照（包含发行价信息）
batch_size = 200
all_snapshots = {}

for i in range(0, len(codes), batch_size):
    batch = codes[i:i+batch_size]
    ret, data = quote_ctx.get_stock_quote(batch)
    if ret == RET_OK:
        for _, row in data.iterrows():
            code = row.get('code', '').replace('HK.', '')
            all_snapshots[code] = row
    
    time.sleep(0.5)

print(f'Got snapshots for {len(all_snapshots)} stocks')

# 处理每只股票
count = 0
for stock_code, listing_date in stocks:
    try:
        snapshot = all_snapshots.get(stock_code)
        if not snapshot:
            continue
        
        # 获取首日K线
        code = f'HK.{stock_code}'
        ret, kline = quote_ctx.get_history_kline(
            code, 
            start=str(listing_date), 
            end=str(listing_date), 
            ktype=KType.K_DAY
        )
        
        first_day_close = None
        first_day_open = None
        first_day_high = None
        first_day_low = None
        first_day_volume = None
        
        if ret == RET_OK and not kline.empty:
            row = kline.iloc[0]
            first_day_close = row.get('close')
            first_day_open = row.get('open')
            first_day_high = row.get('high')
            first_day_low = row.get('low')
            first_day_volume = row.get('volume')
        
        # 当前价格
        cur_price = snapshot.get('last_price', None)
        
        # 更新数据库 - 只更新有数据的字段
        cur.execute("""
            UPDATE stock_ipo SET
                first_day_close = %s,
                first_day_open = %s,
                first_day_high = %s,
                first_day_low = %s,
                first_day_volume = %s,
                current_price = %s,
                updated_at = NOW()
            WHERE stock_code = %s
        """, (first_day_close, first_day_open, first_day_high, first_day_low, 
              first_day_volume, cur_price, stock_code))
        
        count += 1
        if count % 30 == 0:
            print(f'Progress: {count}/{len(stocks)}')
            conn.commit()
        
        time.sleep(0.05)
        
    except Exception as e:
        continue

conn.commit()
print(f'Updated {count} stocks')

# 显示部分数据
cur.execute("""
    SELECT stock_code, stock_name, listing_date, 
           first_day_open, first_day_close, current_price
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01' AND first_day_close IS NOT NULL
    ORDER BY listing_date DESC
    LIMIT 10
""")
rows = cur.fetchall()
if rows:
    print('\nSample data with prices:')
    for row in rows:
        print(f'  {row[0]} {row[1]} | Listed: {row[2]} | Open: {row[3]} | Close: {row[4]} | Now: {row[5]}')

cur.close()
conn.close()
quote_ctx.close()
print('\nDone!')
