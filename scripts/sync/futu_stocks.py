#!/usr/bin/env python3
"""通过Futu获取港股历史IPO数据"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from futu import *

print('Connecting to Futu OpenD...')
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
print('Connected!')

# 获取港股全部股票列表
print('\nGetting HK stock list...')
ret, data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK)
if ret == RET_OK:
    print(f'Got {len(data)} HK stocks')
    print(f'Columns: {data.columns.tolist()}')
    
    # 过滤出2025年至今上市的股票
    # list_time字段应该有上市日期
    if 'list_time' in data.columns:
        # 转换日期格式
        data['list_time'] = data['list_time'].astype(str)
        
        # 过滤2025年至今
        filtered = data[data['list_time'].str.startswith('2025') | data['list_time'].str.startswith('2026')]
        print(f'\nStocks listed since 2025: {len(filtered)}')
        
        # 显示前20条
        print('\nFirst 20 records:')
        for i, row in filtered.head(20).iterrows():
            code = row.get('code', '')
            name = row.get('name', '')
            list_time = row.get('list_time', '')
            print(f'  {code} - {name} | 上市: {list_time}')
        
        # 保存到CSV
        filtered.to_csv('hk_stocks_2025_2026.csv', index=False, encoding='utf-8-sig')
        print(f'\nSaved to hk_stocks_2025_2026.csv ({len(filtered)} records)')
    else:
        print(f'\nNo list_time column. Available columns: {data.columns.tolist()}')
        print('\nSample data:')
        print(data.head(5).to_string())
else:
    print(f'Error: {data}')

quote_ctx.close()
