#!/usr/bin/env python3
"""通过Futu获取完整的港股IPO数据"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import psycopg2
from futu import *
import time

print('Connecting to Futu OpenD...')
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
print('Connected!')

# 连接数据库
conn = psycopg2.connect(
    host="localhost", port=5432, database="hk_stock",
    user="postgres", password="pc20050218"
)
cur = conn.cursor()

# 获取所有IPO股票代码
cur.execute("SELECT stock_code, stock_name, listing_date FROM stock_ipo WHERE listing_date >= '2025-01-01' ORDER BY listing_date")
stocks = cur.fetchall()
print(f'Found {len(stocks)} IPO stocks in database')

# 获取每只股票的详细信息
count = 0
for stock_code, stock_name, listing_date in stocks:
    try:
        code = f'HK.{stock_code}'
        
        # 获取IPO详情
        ret, ipo_data = quote_ctx.get_ipo_list(Market.HK)
        if ret == RET_OK and not ipo_data.empty:
            # 查找当前股票
            ipo_info = ipo_data[ipo_data['code'] == code]
            if not ipo_info.empty:
                row = ipo_info.iloc[0]
                ipo_price = row.get('ipo_price', None)
                winning_ratio = row.get('winning_ratio', None)
                issue_size = row.get('issue_size', None)
                entrance_price = row.get('entrance_price', None)
                
                # 转换数据
                if ipo_price and ipo_price != 'N/A':
                    try:
                        ipo_price = float(ipo_price)
                    except:
                        ipo_price = None
                else:
                    ipo_price = None
                    
                if winning_ratio and winning_ratio != 'N/A':
                    try:
                        winning_ratio = float(winning_ratio)
                    except:
                        winning_ratio = None
                else:
                    winning_ratio = None
        
        # 获取首日收盘价（计算涨跌幅）
        ret2, kline_data = quote_ctx.get_history_kline(code, start=str(listing_date), end=str(listing_date), ktype=KType.K_DAY)
        first_day_close = None
        first_day_change = None
        
        if ret2 == RET_OK and not kline_data.empty:
            first_day_close = kline_data.iloc[0].get('close', None)
            if ipo_price and first_day_close and ipo_price > 0:
                first_day_change = round((first_day_close - ipo_price) / ipo_price * 100, 2)
        
        # 更新数据库
        cur.execute("""
            UPDATE stock_ipo SET
                issue_price = COALESCE(%s, issue_price),
                allotment_rate = COALESCE(%s, allotment_rate),
                entry_fee = COALESCE(%s, entry_fee),
                first_day_change = COALESCE(%s, first_day_change),
                updated_at = NOW()
            WHERE stock_code = %s
        """, (ipo_price, winning_ratio, entrance_price, first_day_change, stock_code))
        
        count += 1
        if count % 20 == 0:
            print(f'Progress: {count}/{len(stocks)}')
            conn.commit()
        
        time.sleep(0.1)  # 避免请求过快
        
    except Exception as e:
        continue

conn.commit()
print(f'\nUpdated {count} stocks')

# 验证数据
cur.execute("""
    SELECT 
        COUNT(*) as total,
        COUNT(issue_price) as has_price,
        COUNT(allotment_rate) as has_winning,
        COUNT(first_day_change) as has_change
    FROM stock_ipo WHERE listing_date >= '2025-01-01'
""")
row = cur.fetchone()
print(f'\nData completeness:')
print(f'  Total: {row[0]}')
print(f'  Has issue price: {row[1]}')
print(f'  Has winning rate: {row[2]}')
print(f'  Has first day change: {row[3]}')

# 显示部分数据
cur.execute("""
    SELECT stock_code, stock_name, listing_date, issue_price, allotment_rate, first_day_change
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01'
    ORDER BY listing_date DESC
    LIMIT 10
""")
print('\nLatest 10 stocks:')
for row in cur.fetchall():
    print(f'  {row[0]} {row[1]} | {row[2]} | Price: {row[3]} | Winning: {row[4]}% | Change: {row[5]}%')

cur.close()
conn.close()
quote_ctx.close()
print('\nDone!')
