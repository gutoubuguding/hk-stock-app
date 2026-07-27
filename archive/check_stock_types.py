#!/usr/bin/env python3
"""Check stock types from Futu OpenD"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from futu import OpenQuoteContext, RET_OK, Market

FUTU_HOST = 'host.docker.internal'
FUTU_PORT = 11111

quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)
ret, data = quote_ctx.get_stock_basicinfo(Market.HK)
quote_ctx.close()

print(f'Total stocks: {len(data)}')
print(f'Columns: {data.columns.tolist()}')
print(f'Stock type values: {data["stock_type"].unique()}')
print(f'Stock type counts:')
print(data['stock_type'].value_counts())
print(f'\nFirst 5 rows:')
print(data.head())
