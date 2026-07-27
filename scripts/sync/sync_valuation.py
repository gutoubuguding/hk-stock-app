#!/usr/bin/env python3
"""同步港股估值数据(PE/PB/股息率/市值)"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import akshare as ak
import psycopg2
import os
from datetime import datetime
import time

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

print("=" * 50)
print("同步港股估值数据")
print("=" * 50)

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# 获取有K线数据的股票
cur.execute("""
    SELECT DISTINCT stock_code, stock_name 
    FROM stock_info 
    WHERE stock_code IN (SELECT DISTINCT stock_code FROM stock_kline WHERE period_type='D')
    ORDER BY stock_code
""")
stocks = cur.fetchall()
total = len(stocks)
print(f"需要同步估值: {total} 只股票")

synced = 0
failed = 0
start = time.time()

for i, (code, name) in enumerate(stocks, 1):
    try:
        # 使用AKShare获取个股信息
        df = ak.stock_hk_spot_em()
        if df is None or df.empty:
            failed += 1
            continue
        
        # 查找该股票
        row = df[df['代码'] == code]
        if row.empty:
            failed += 1
            continue
        
        row = row.iloc[0]
        
        # 提取估值数据
        pe = float(row.get('市盈率-动态', 0)) if row.get('市盈率-动态') and str(row.get('市盈率-动态')) != '-' else None
        pb = float(row.get('市净率', 0)) if row.get('市净率') and str(row.get('市净率')) != '-' else None
        dividend_yield = float(row.get('股息率', 0)) if row.get('股息率') and str(row.get('股息率')) != '-' else None
        market_cap = float(row.get('总市值', 0)) if row.get('总市值') and str(row.get('总市值')) != '-' else None
        
        if pe is not None or pb is not None or market_cap is not None:
            cur.execute('''
                INSERT INTO stock_valuation (stock_code, pe, pb, dividend_yield, market_cap, data_date, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (stock_code, data_date) DO UPDATE SET
                    pe = EXCLUDED.pe, pb = EXCLUDED.pb,
                    dividend_yield = EXCLUDED.dividend_yield,
                    market_cap = EXCLUDED.market_cap,
                    updated_at = EXCLUDED.updated_at
            ''', (code, pe, pb, dividend_yield, market_cap, datetime.now().date(), datetime.now()))
            conn.commit()
            synced += 1
        
        if i % 100 == 0:
            elapsed = time.time() - start
            print(f"进度: {i}/{total} | 成功: {synced} | 失败: {failed}")
        
    except Exception as e:
        failed += 1
        if i <= 5:
            print(f"  {code} 失败: {e}")
    
    time.sleep(0.1)

cur.execute("SELECT COUNT(*) FROM stock_valuation")
final_count = cur.fetchone()[0]
cur.close()
conn.close()

elapsed = time.time() - start
print(f"\n{'='*50}")
print(f"完成！耗时: {elapsed/60:.1f}分钟")
print(f"成功: {synced} | 失败: {failed}")
print(f"估值记录总数: {final_count}")
print(f"{'='*50}")
