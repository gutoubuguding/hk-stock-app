#!/usr/bin/env python3
"""通过Futu OpenD获取港股IPO列表"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from futu import *

print('Connecting to Futu OpenD...')
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
print('Connected!')

# 获取港股IPO列表
print('\nGetting HK IPO list...')
ret, data = quote_ctx.get_ipo_list(Market.HK)
if ret == RET_OK:
    print(f'Got {len(data)} IPO records')
    print(f'Columns: {data.columns.tolist()}')
    print('\nFirst 20 records:')
    for i, row in data.head(20).iterrows():
        code = row.get('code', '')
        name = row.get('name', '')
        list_time = row.get('list_time', '')
        ipo_price = row.get('ipo_price', '')
        print(f'  {code} - {name} | 上市: {list_time} | 发行价: {ipo_price}')
    
    # 保存到CSV
    data.to_csv('futu_ipo_list.csv', index=False, encoding='utf-8-sig')
    print(f'\nSaved to futu_ipo_list.csv ({len(data)} records)')
else:
    print(f'Error: {data}')

quote_ctx.close()
