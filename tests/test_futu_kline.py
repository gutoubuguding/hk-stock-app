#!/usr/bin/env python3
"""Test Futu OpenD history K-line retrieval"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
sys.stdout.reconfigure(encoding='utf-8')

from futu import *

HOST = '127.0.0.1'
PORT = 11111

print(f"Connecting to Futu OpenD at {HOST}:{PORT}...")

quote_ctx = OpenQuoteContext(host=HOST, port=PORT, is_encrypt=False)
print(f"Context status: {quote_ctx.status}")

# Test: Get history K-line for 00700 (Tencent)
stock_code = "HK.00700"

print(f"\nFetching daily K-line for {stock_code}...")
ret, data, page_req_key = quote_ctx.request_history_kline(
    code=stock_code,
    start="2026-03-01",
    end="2026-04-20",
    ktype=KLType.K_DAY,
    autype=AuType.QFQ  # 前复权
)

print(f"Return code: {ret}")
if ret != RET_OK:
    print(f"Error: {data}")
else:
    print(f"Data shape: {data.shape}")
    print(f"Columns: {list(data.columns)}")
    print(f"\nLast 5 rows:")
    print(data.tail().to_string())

quote_ctx.close()
print("\nDone.")