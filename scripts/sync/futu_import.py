#!/usr/bin/env python3
"""通过Futu获取港股2025年至今上市的股票"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import psycopg2
from futu import *

print('Connecting to Futu OpenD...')
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
print('Connected!')

# 获取港股全部股票列表
print('\nGetting HK stock list...')
ret, data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK)
if ret == RET_OK:
    print(f'Got {len(data)} HK stocks')
    
    # 转换listing_date为字符串
    data['listing_date'] = data['listing_date'].astype(str)
    
    # 过滤2025年至今上市的股票
    filtered = data[
        (data['listing_date'] >= '2025-01-01') & 
        (data['listing_date'] <= '2026-12-31') &
        (data['stock_type'] == 'STOCK')  # 只要股票，不要其他类型
    ].copy()
    
    print(f'\nStocks listed 2025-01-01 to 2026-12-31: {len(filtered)}')
    
    # 按上市日期排序
    filtered = filtered.sort_values('listing_date', ascending=False)
    
    # 显示前30条
    print('\nLatest 30 stocks:')
    for i, row in filtered.head(30).iterrows():
        code = row.get('code', '').replace('HK.', '')
        name = row.get('name', '')
        list_date = row.get('listing_date', '')
        print(f'  {code} - {name} | {list_date}')
    
    # 保存到CSV
    filtered.to_csv('hk_ipo_2025_2026.csv', index=False, encoding='utf-8-sig')
    print(f'\nSaved to hk_ipo_2025_2026.csv ({len(filtered)} records)')
    
    # 导入数据库
    print('\nImporting to database...')
    conn = psycopg2.connect(
        host="localhost", port=5432, database="hk_stock",
        user="postgres", password="pc20050218"
    )
    cur = conn.cursor()
    
    # 清空现有数据
    cur.execute("DELETE FROM stock_ipo WHERE listing_date >= '2025-01-01'")
    
    count = 0
    for i, row in filtered.iterrows():
        code = row.get('code', '').replace('HK.', '')
        name = row.get('name', '')
        list_date = row.get('listing_date', '')
        
        cur.execute("""
            INSERT INTO stock_ipo (stock_code, stock_name, listing_date, updated_at)
            VALUES (%s, %s, %s, NOW())
        """, (code, name, list_date))
        count += 1
    
    conn.commit()
    print(f'Inserted {count} IPO records')
    
    # 验证
    cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01'")
    total = cur.fetchone()[0]
    print(f'Total in database: {total}')
    
    cur.close()
    conn.close()
else:
    print(f'Error: {data}')

quote_ctx.close()
print('\nDone!')
