#!/usr/bin/env python3
"""Verify both 需求4 and 需求7 are working"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
sys.stdout.reconfigure(encoding='utf-8')

import psycopg2

DB = {"host": "localhost", "port": 5432, "dbname": "hk_stock", "user": "postgres", "password": "pc20050218"}
conn = psycopg2.connect(**DB)
cur = conn.cursor()

print("=" * 60)
print("需求4：大盘概览 - market_overview表")
print("=" * 60)
cur.execute("SELECT COUNT(*) FROM market_overview")
print(f"market_overview 记录数: {cur.fetchone()[0]}")
cur.execute("""
    SELECT index_code, index_name, last_price, change_val, change_pct, raise_count, fall_count
    FROM market_overview ORDER BY update_time DESC LIMIT 3
""")
for r in cur.fetchall():
    print(f"  {r[0]} {r[1]}: {r[2]} ({r[3]:+.2f}, {r[4]:+.2f}%) 涨跌家数={r[5]}/{r[6]}")

print()
print("=" * 60)
print("需求7：估值指标 - stock_valuation表")
print("=" * 60)
cur.execute("SELECT COUNT(*) FROM stock_valuation")
print(f"stock_valuation 记录数: {cur.fetchone()[0]}")

cur.execute("""
    SELECT stock_code, pe, pb, dividend_yield, market_cap
    FROM stock_valuation WHERE data_date = CURRENT_DATE
    LIMIT 10
""")
print("\n今日估值数据样本:")
for r in cur.fetchall():
    print(f"  {r[0]}: PE={r[1]}, PB={r[2]}, 股息率={r[3]}%, 市值={r[4]:,.0f}")

# Check API endpoint directly
import urllib.request
import json
try:
    req = urllib.request.urlopen('http://localhost:8080/api/calendar/market-overview', timeout=5)
    data = json.loads(req.read())
    print("\n\nDashboard API 响应:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"\n\nAPI调用失败: {e}")

cur.close(); conn.close()