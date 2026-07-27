#!/usr/bin/env python3
"""通过Futu获取IPO股票价格（需要先订阅）"""
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
cur.execute("SELECT stock_code, stock_name, listing_date FROM stock_ipo WHERE listing_date >= '2025-01-01' ORDER BY listing_date")
stocks = cur.fetchall()
print(f'Processing {len(stocks)} stocks...')

codes = [f'HK.{s[0]}' for s in stocks]

# 分批订阅和获取数据
batch_size = 50
all_data = {}

for i in range(0, len(codes), batch_size):
    batch = codes[i:i+batch_size]
    
    # 订阅股票
    ret = quote_ctx.subscribe(batch, [SubType.QUOTE])
    if ret != RET_OK:
        print(f'Subscribe failed for batch {i//batch_size}')
        continue
    
    time.sleep(0.5)
    
    # 获取快照
    ret, data = quote_ctx.get_stock_quote(batch)
    if ret == RET_OK:
        for _, row in data.iterrows():
            code = row.get('code', '').replace('HK.', '')
            all_data[code] = {
                'open': row.get('open_price'),
                'close': row.get('last_price'),
                'high': row.get('high_price'),
                'low': row.get('low_price'),
                'volume': row.get('volume'),
                'price_spread': row.get('price_spread'),
            }
    
    # 取消订阅
    quote_ctx.unsubscribe(batch, [SubType.QUOTE])
    time.sleep(0.3)
    
    print(f'Batch {i//batch_size + 1}: {len(all_data)} stocks')

print(f'\nGot data for {len(all_data)} stocks')

# 更新数据库
count = 0
for stock_code, stock_name, listing_date in stocks:
    try:
        data = all_data.get(stock_code)
        if not data:
            continue
        
        cur.execute("""
            UPDATE stock_ipo SET
                current_price = %s,
                updated_at = NOW()
            WHERE stock_code = %s
        """, (data['close'], stock_code))
        
        count += 1
        
    except Exception as e:
        continue

conn.commit()
print(f'Updated {count} stocks with current prices')

# 获取首日K线数据
print('\nFetching first-day K-line data...')
count2 = 0
for stock_code, stock_name, listing_date in stocks[:30]:  # 先测试30只
    try:
        code = f'HK.{stock_code}'
        ret, kline = quote_ctx.get_history_kline(
            code,
            start=str(listing_date),
            end=str(listing_date),
            ktype=KType.K_DAY,
            autype=AuType.NONE
        )
        
        if ret == RET_OK and not kline.empty:
            row = kline.iloc[0]
            first_day_open = row.get('open')
            first_day_close = row.get('close')
            first_day_high = row.get('high')
            first_day_low = row.get('low')
            first_day_volume = row.get('volume')
            
            cur.execute("""
                UPDATE stock_ipo SET
                    first_day_open = %s,
                    first_day_close = %s,
                    first_day_high = %s,
                    first_day_low = %s,
                    first_day_volume = %s,
                    updated_at = NOW()
                WHERE stock_code = %s
            """, (first_day_open, first_day_close, first_day_high, first_day_low, first_day_volume, stock_code))
            
            count2 += 1
        
        time.sleep(0.1)
        
    except Exception as e:
        continue

conn.commit()
print(f'Updated {count2} stocks with first-day data')

# 验证
cur.execute("""
    SELECT stock_code, stock_name, listing_date, 
           first_day_open, first_day_close, current_price
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01' 
    ORDER BY listing_date DESC
    LIMIT 10
""")
rows = cur.fetchall()
print('\nSample data:')
for row in rows:
    print(f'  {row[0]} {row[1]} | {row[2]} | Open: {row[3]} | Close: {row[4]} | Now: {row[5]}')

cur.close()
conn.close()
quote_ctx.close()
print('\nDone!')
