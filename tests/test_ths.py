#!/usr/bin/env python3
"""测试 stock_ipo_hk_ths 接口"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False
import sys
sys.stdout.reconfigure(encoding='utf-8')

import akshare as ak

df = ak.stock_ipo_hk_ths()
print(f"Total rows: {len(df)}")
print(f"\nColumns:")
for i, col in enumerate(df.columns):
    print(f"  [{i}] {repr(col)}")

print(f"\nFirst 5 rows:")
for i in range(min(5, len(df))):
    print(f"\n--- Row {i} ---")
    for j, val in enumerate(df.iloc[i]):
        print(f"  [{j}]: {repr(val)}")
