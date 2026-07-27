#!/usr/bin/env python3
"""Test Futu OpenD for market overview and stock quotes with valuation"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

from futu import *

HOST = '127.0.0.1'
PORT = 11111

print("=== 1. 测试获取恒生指数数据 ===")
quote_ctx = OpenQuoteContext(host=HOST, port=PORT, is_encrypt=False)

# 恒生指数代码: HK.800000 (HSI), HK.800001 (HSTECH), HK.800002 (HSCEI)
index_codes = ["HK.800000", "HK.800001", "HK.800002", "HK.800003"]
for code in index_codes:
    ret, data = quote_ctx.get_market_snapshot([code])
    print(f"\n{code}:")
    print(f"  Return: {ret}")
    if ret == RET_OK and data is not None:
        print(f"  Data: {data.to_string()}")
    else:
        print(f"  Error: {data}")

print("\n=== 2. 测试获取股票实时报价(含估值) ===")
stock_codes = ["HK.00700", "HK.09988", "HK.00005"]
ret, data = quote_ctx.get_market_snapshot(stock_codes)
print(f"Return: {ret}")
if ret == RET_OK and data is not None:
    print(f"Columns: {list(data.columns)}")
    print(data.to_string())
else:
    print(f"Error: {data}")

print("\n=== 3. 测试获取基本信息(含PE/PB等) ===")
ret, data = quote_ctx.get_stock_quote(["HK.00700", "HK.09988"])
print(f"Return: {ret}")
if ret == RET_OK and data is not None:
    print(f"Columns: {list(data.columns)}")
    print(data.to_string())
else:
    print(f"Error: {data}")

quote_ctx.close()
print("\nDone.")