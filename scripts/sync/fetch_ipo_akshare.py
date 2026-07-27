#!/usr/bin/env python3
"""通过akshare获取港股IPO股票的历史价格"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False

import akshare as ak
import psycopg2
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = psycopg2.connect(
    host="localhost", port=5432, database="hk_stock",
    user="postgres", password="pc20050218"
)
cur = conn.cursor()

# 获取IPO股票列表
cur.execute("SELECT stock_code, stock_name, listing_date FROM stock_ipo WHERE listing_date >= '2025-01-01' ORDER BY listing_date")
stocks = cur.fetchall()
print(f'Processing {len(stocks)} stocks...')

count = 0
for stock_code, stock_name, listing_date in stocks:
    try:
        # 获取历史K线数据
        df = ak.stock_hk_daily(symbol=stock_code, adjust='')
        
        if df.empty:
            continue
        
        # 转换日期列
        df['date'] = df['date'].astype(str)
        
        # 获取上市首日数据
        first_day = df[df['date'] == str(listing_date)]
        
        if not first_day.empty:
            row = first_day.iloc[0]
            first_day_open = float(row['open']) if row['open'] else None
            first_day_close = float(row['close']) if row['close'] else None
            first_day_high = float(row['high']) if row['high'] else None
            first_day_low = float(row['low']) if row['low'] else None
            first_day_volume = int(row['volume']) if row['volume'] else None
            
            # 获取最新价格
            latest = df.iloc[-1]
            current_price = float(latest['close']) if latest['close'] else None
            
            # 计算涨跌幅
            first_day_change = None
            current_change = None
            
            if first_day_open and first_day_close:
                first_day_change = round((first_day_close - first_day_open) / first_day_open * 100, 2)
            
            if first_day_open and current_price:
                current_change = round((current_price - first_day_open) / first_day_open * 100, 2)
            
            # 更新数据库
            cur.execute("""
                UPDATE stock_ipo SET
                    first_day_open = %s,
                    first_day_close = %s,
                    first_day_high = %s,
                    first_day_low = %s,
                    first_day_volume = %s,
                    current_price = %s,
                    first_day_change = %s,
                    current_change = %s,
                    updated_at = NOW()
                WHERE stock_code = %s
            """, (first_day_open, first_day_close, first_day_high, first_day_low,
                  first_day_volume, current_price, first_day_change, current_change, stock_code))
            
            count += 1
        
        time.sleep(0.3)
        
        if count % 20 == 0:
            print(f'Progress: {count} stocks processed')
            conn.commit()
    
    except Exception as e:
        continue

conn.commit()
print(f'\nUpdated {count} stocks with price data')

# 验证
cur.execute("""
    SELECT stock_code, stock_name, listing_date, 
           first_day_open, first_day_close, current_price, 
           first_day_change, current_change
    FROM stock_ipo 
    WHERE listing_date >= '2025-01-01' AND first_day_close IS NOT NULL
    ORDER BY listing_date DESC
    LIMIT 15
""")
rows = cur.fetchall()
print('\nSample data (stocks with prices):')
for row in rows:
    print(f'  {row[0]} {row[1]} | Listed: {row[2]} | Open: {row[3]} | Close: {row[4]} | Now: {row[5]} | Day1: {row[6]}% | Total: {row[7]}%')

cur.close()
conn.close()
print('\nDone!')
