#!/usr/bin/env python3
"""修正首日涨跌幅 - 通过AKShare获取真实首日收盘价计算"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False

import psycopg2
import akshare as ak
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

def get_first_day_change(stock_code, issue_price, listing_date):
    """获取新股上市首日收盘价，计算涨跌幅"""
    if not issue_price or not listing_date:
        return None
    
    try:
        # 使用AKShare获取历史K线数据
        df = ak.stock_hk_daily(symbol=stock_code, adjust='')
        if df is None or df.empty:
            return None
        
        df['date'] = df['date'].astype(str)
        
        # 找到上市首日的数据
        first_day_data = df[df['date'] == str(listing_date)]
        
        if first_day_data.empty:
            return None
        
        first_close = float(first_day_data.iloc[0]['close'])
        
        # 计算首日涨跌幅
        change = round((first_close - issue_price) / issue_price * 100, 2)
        return change
        
    except Exception as e:
        return None

def main():
    # 获取所有有发行价但首日涨跌幅是错误数据的股票
    cur.execute("""
        SELECT stock_code, stock_name, issue_price, listing_date, first_day_change
        FROM stock_ipo 
        WHERE listing_date >= '2025-01-01'
        AND issue_price IS NOT NULL
        AND listing_date IS NOT NULL
        AND (first_day_change IS NULL OR first_day_change = 100)
        ORDER BY listing_date DESC
    """)
    stocks = cur.fetchall()
    print(f"需要修正的股票数量: {len(stocks)}")
    
    success = 0
    failed = 0
    
    for idx, (code, name, issue_price, listing_date, old_change) in enumerate(stocks):
        print(f"[{idx+1}/{len(stocks)}] {code} {name} | 发行价:{issue_price} | 上市日:{listing_date}")
        
        new_change = get_first_day_change(code, float(issue_price), listing_date)
        
        if new_change is not None:
            cur.execute("""
                UPDATE stock_ipo 
                SET first_day_change = %s, updated_at = NOW()
                WHERE stock_code = %s
            """, (new_change, code))
            print(f"  -> 首日涨跌: {new_change}%")
            success += 1
        else:
            print(f"  -> 获取失败")
            failed += 1
        
        time.sleep(0.3)
    
    conn.commit()
    print(f"\n修正完成: 成功={success}, 失败={failed}")

if __name__ == '__main__':
    main()