#!/usr/bin/env python3
"""Test sync with small batch first"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

import psycopg2
import time
from futu import *

DB_CONFIG = {
    "host": "localhost", "port": 5432, "dbname": "hk_stock",
    "user": "postgres", "password": "pc20050218"
}

FUTU_HOST = '127.0.0.1'
FUTU_PORT = 11111

def get_latest_date(conn, stock_code):
    cur = conn.cursor()
    cur.execute("""
        SELECT trade_date FROM stock_kline 
        WHERE stock_code = %s AND period_type = 'D'
        ORDER BY trade_date DESC LIMIT 1
    """, (stock_code,))
    result = cur.fetchone()
    cur.close()
    return result[0] if result else None

def sync_stock_kline(quote_ctx, conn, stock_code_hk, stock_code_raw):
    cur = conn.cursor()
    
    try:
        latest = get_latest_date(conn, stock_code_raw)
        
        if latest:
            from datetime import datetime, timedelta
            start_date = (datetime.strptime(str(latest), '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
        else:
            start_date = "2025-01-01"
        
        end_date = "2026-04-21"
        
        if start_date >= end_date:
            cur.close()
            return 0, 0
        
        ret, data, page_key = quote_ctx.request_history_kline(
            code=stock_code_hk,
            start=start_date,
            end=end_date,
            ktype=KLType.K_DAY,
            autype=AuType.QFQ
        )
        
        if ret != RET_OK:
            return 0, 1
        
        if data is None or data.empty:
            cur.close()
            return 0, 0
        
        count = 0
        for _, row in data.iterrows():
            td = row['time_key'][:10]
            op = float(row['open'])
            cp = float(row['close'])
            hp = float(row['high'])
            lp = float(row['low'])
            vol = int(row['volume'])
            tov = float(row['turnover'])
            chg = float(row['change_rate'])
            
            cur.execute("""
                INSERT INTO stock_kline 
                (stock_code, period_type, trade_date, open_price, close_price, 
                 high_price, low_price, volume, turnover, change_percent, turnover_rate)
                VALUES (%s, 'D', %s, %s, %s, %s, %s, %s, %s, %s, 0)
                ON CONFLICT (stock_code, period_type, trade_date) DO UPDATE SET
                    open_price = EXCLUDED.open_price,
                    close_price = EXCLUDED.close_price,
                    high_price = EXCLUDED.high_price,
                    low_price = EXCLUDED.low_price,
                    volume = EXCLUDED.volume,
                    turnover = EXCLUDED.turnover,
                    change_percent = EXCLUDED.change_percent
            """, (stock_code_raw, td, op, cp, hp, lp, vol, tov, chg))
            
            if cur.rowcount > 0:
                count += 1
        
        conn.commit()
        cur.close()
        return count, 0
        
    except Exception as e:
        conn.rollback()
        cur.close()
        return 0, 1

conn = psycopg2.connect(**DB_CONFIG)
quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

# Test with 10 stocks
test_codes = ["HK.00700", "HK.09988", "HK.03690", "HK.01810", "HK.00005",
              "HK.01299", "HK.02318", "HK.00941", "HK.03988", "HK.02020"]

print(f"Testing with {len(test_codes)} stocks...")
total_new = 0
total_fail = 0

for stock_code_hk in test_codes:
    stock_code_raw = stock_code_hk.replace("HK.", "")
    count, err = sync_stock_kline(quote_ctx, conn, stock_code_hk, stock_code_raw)
    
    latest = get_latest_date(psycopg2.connect(**DB_CONFIG), stock_code_raw)
    
    if err == 0:
        print(f"  ✅ {stock_code_raw}: 新增{count}条 最新日期{latest}")
        total_new += count
    else:
        print(f"  ❌ {stock_code_raw}: 失败")
        total_fail += 1
    
    time.sleep(0.3)

print(f"\n测试完成: 新增{total_new}条, 失败{total_fail}只")

quote_ctx.close()