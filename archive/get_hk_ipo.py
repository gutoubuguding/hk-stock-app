#!/usr/bin/env python3
"""从同花顺获取港股IPO数据"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False
import sys
sys.stdout.reconfigure(encoding='utf-8')

import akshare as ak

# 获取港股IPO数据
df = ak.stock_ipo_hk_ths()
print(f"Total records: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print()

# 显示所有数据
for i, row in df.iterrows():
    code = row.iloc[0]  # 股票代码
    name = row.iloc[1]  # 股票简称
    listing_date = row.iloc[14] if len(row) > 14 else '-'  # 上市日期
    
    print(f"{i+1}. {code} - {name} | 上市: {listing_date}")
