#!/usr/bin/env python3
"""用已有K线数据计算IPO涨跌幅"""
import sys
import os
os.environ['NO_PROXY'] = '*'

sys.stdout.reconfigure(encoding='utf-8')
import psycopg2
from datetime import datetime, timedelta

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

def main():
    print("用已有K线数据计算IPO涨跌幅...")
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 获取需要计算涨跌幅的IPO
    cur.execute("""
        SELECT stock_code, stock_name, listing_date, issue_price
        FROM stock_ipo
        WHERE listing_date IS NOT NULL
          AND issue_price IS NOT NULL
          AND issue_price > 0
        ORDER BY listing_date DESC
    """)
    ipos = cur.fetchall()
    print(f"找到 {len(ipos)} 只有发行价的IPO")
    
    updated = 0
    for stock_code, stock_name, listing_date, issue_price in ipos:
        try:
            # 获取上市后的K线数据
            cur.execute("""
                SELECT trade_date, close_price
                FROM stock_kline
                WHERE stock_code = %s
                  AND period_type = 'D'
                  AND trade_date >= %s
                ORDER BY trade_date ASC
            """, (stock_code, listing_date))
            klines = cur.fetchall()
            
            if not klines:
                continue
            
            # 转换issue_price为float
            issue_price = float(issue_price)
            
            # 计算涨跌幅
            first_day_change = None
            seven_day_change = None
            thirty_day_change = None
            current_change = None
            
            # 首日涨跌幅
            if len(klines) >= 1:
                first_close = float(klines[0][1])
                first_day_change = round((first_close - issue_price) / issue_price * 100, 2)
            
            # 7天涨跌幅
            if len(klines) >= 7:
                seven_close = float(klines[6][1])
                seven_day_change = round((seven_close - issue_price) / issue_price * 100, 2)
            
            # 30天涨跌幅
            if len(klines) >= 30:
                thirty_close = float(klines[29][1])
                thirty_day_change = round((thirty_close - issue_price) / issue_price * 100, 2)
            
            # 现价涨跌幅（最新收盘价）
            latest_close = float(klines[-1][1])
            current_change = round((latest_close - issue_price) / issue_price * 100, 2)
            
            # 更新数据库
            cur.execute("""
                UPDATE stock_ipo
                SET first_day_change = %s,
                    seven_day_change = %s,
                    thirty_day_change = %s,
                    current_change = %s,
                    current_price = %s,
                    updated_at = NOW()
                WHERE stock_code = %s
            """, (first_day_change, seven_day_change, thirty_day_change, current_change, latest_close, stock_code))
            
            if cur.rowcount > 0:
                updated += 1
                if updated % 10 == 0:
                    print(f"  已更新 {updated} 只...")
                    conn.commit()
            
        except Exception as e:
            print(f"  {stock_code} {stock_name} 计算失败: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"\n完成！更新了 {updated} 只IPO的涨跌幅")

if __name__ == '__main__':
    main()
