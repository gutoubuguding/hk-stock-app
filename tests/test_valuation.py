#!/usr/bin/env python3
"""Test valuation sync for 10 stocks"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

import psycopg2
from datetime import date
from futu import *

DB_CONFIG = {
    "host": "localhost", "port": 5432, "dbname": "hk_stock",
    "user": "postgres", "password": "pc20050218"
}

FUTU_HOST = '127.0.0.1'
FUTU_PORT = 11111

quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

test_codes = ["HK.00700", "HK.09988", "HK.03690", "HK.01810", "HK.00005",
              "HK.01299", "HK.02318", "HK.00941", "HK.03988", "HK.02020"]

ret, data = quote_ctx.get_market_snapshot(test_codes)
print(f"Return: {ret}")
if ret == RET_OK and data is not None:
    print(f"Got {len(data)} rows")
    for _, row in data.iterrows():
        code = row['code'].replace('HK.', '')
        pe = row['pe_ratio'] if row['pe_ratio'] else 'N/A'
        pb = row['pb_ratio'] if row['pb_ratio'] else 'N/A'
        dy = row['dividend_ratio_ttm'] if row['dividend_ratio_ttm'] else 'N/A'
        mc = row['total_market_val'] if row['total_market_val'] else 0
        print(f"  {code}: PE={pe} PB={pb} 股息率={dy}% 市值={mc:,.0f}")
else:
    print(f"Error: {data}")

quote_ctx.close()