#!/usr/bin/env python3
"""使用Futu API同步估值数据"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from futu import OpenQuoteContext, RET_OK
import psycopg2
import os
import time

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

FUTU_HOST = os.getenv('FUTU_OPEND_HOST', 'host.docker.internal')
FUTU_PORT = int(os.getenv('FUTU_OPEND_PORT', '11111'))

print("=" * 50)
print("使用Futu API同步估值数据")
print("=" * 50)

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# 获取有K线的主要股票
cur.execute("""
    SELECT DISTINCT stock_code 
    FROM stock_kline 
    WHERE period_type = 'D'
    ORDER BY stock_code
    LIMIT 500
""")
stocks = cur.fetchall()
total = len(stocks)
print(f"需要同步估值: {total} 只股票")

quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

synced = 0
failed = 0
start = time.time()

# 分批获取（每批最多100只）
BATCH_SIZE = 50
for batch_start in range(0, total, BATCH_SIZE):
    batch = stocks[batch_start:batch_start + BATCH_SIZE]
    codes = [f"HK.{s[0]}" for s in batch]
    
    try:
        # 获取基本行情（包含市值等）
        ret, data = quote_ctx.get_market_snapshot(codes)
        if ret == RET_OK:
            for _, row in data.iterrows():
                code = row['code'].replace('HK.', '')
                pe = float(row.get('pe_ratio', 0)) if row.get('pe_ratio') and row['pe_ratio'] != '-' else None
                pb = float(row.get('pb_ratio', 0)) if row.get('pb_ratio') and row['pb_ratio'] != '-' else None
                dividend = float(row.get('dividend_yield', 0)) if row.get('dividend_yield') and row['dividend_yield'] != '-' else None
                market_cap = float(row.get('total_market_val', 0)) if row.get('total_market_val') else None
                
                if pe or pb or market_cap:
                    try:
                        cur.execute('''
                            INSERT INTO stock_valuation (stock_code, pe, pb, dividend_yield, market_cap, data_date, updated_at)
                            VALUES (%s, %s, %s, %s, %s, %s, %s)
                            ON CONFLICT (stock_code, data_date) DO UPDATE SET
                                pe = EXCLUDED.pe, pb = EXCLUDED.pb,
                                dividend_yield = EXCLUDED.dividend_yield,
                                market_cap = EXCLUDED.market_cap,
                                updated_at = EXCLUDED.updated_at
                        ''', (code, pe, pb, dividend, market_cap, time.strftime('%Y-%m-%d'), time.strftime('%Y-%m-%d %H:%M:%S')))
                        synced += 1
                    except:
                        pass
            conn.commit()
        
        print(f"批次 {batch_start//BATCH_SIZE + 1}: 成功 {synced}")
        
    except Exception as e:
        print(f"批次 {batch_start//BATCH_SIZE + 1} 失败: {e}")
        failed += len(batch)
    
    time.sleep(1)

quote_ctx.close()

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
