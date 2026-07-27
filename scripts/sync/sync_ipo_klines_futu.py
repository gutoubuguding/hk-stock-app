#!/usr/bin/env python3
"""
用 Futu OpenD 补全新股K线数据
绕过 akshare 的 IP 限速问题
"""
import sys
import os
os.environ['NO_PROXY'] = '*'

from futu import *
import psycopg2
from datetime import datetime

DB_CONFIG = {
    "host": "localhost", "port": 5432, "dbname": "hk_stock",
    "user": "postgres", "password": "pc20050218"
}

FUTU_HOST = '127.0.0.1'
FUTU_PORT = 11111


def sync_ipo_klines_futu():
    """用Futu API补全新股K线"""
    conn = psycopg2.connect(**DB_CONFIG)
    
    # 获取所有缺失K线的新股（IPO表里有，但stock_info可能没有）
    cur = conn.cursor()
    cur.execute("""
        SELECT DISTINCT i.stock_code, i.stock_name, i.listing_date
        FROM stock_ipo i
        LEFT JOIN stock_kline sk ON i.stock_code = sk.stock_code AND sk.period_type = 'D'
        WHERE sk.stock_code IS NULL OR 
              (SELECT COUNT(*) FROM stock_kline WHERE stock_code = i.stock_code AND period_type = 'D') < 5
        ORDER BY i.listing_date DESC NULLS LAST
    """)
    ipo_stocks = cur.fetchall()
    cur.close()
    
    if not ipo_stocks:
        print("没有需要补全的新股K线")
        conn.close()
        return
    
    print(f"通过 Futu API 补全 {len(ipo_stocks)} 只新股K线...")
    
    quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)
    quote_ctx.set_sync_query_connect_timeout(10)
    
    success = 0
    failed = 0
    
    for code, name, listing_date in ipo_stocks:
        print(f"\n处理: {code} {name} (上市日: {listing_date})")
        
        # Futu代码格式：HK.XXXXX
        futu_code = f"HK.{code}"
        
        # 从上市日开始，最多取2年数据
        if listing_date:
            start_date = listing_date.strftime('%Y-%m-%d')
        else:
            start_date = '2024-01-01'
        
        end_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            ret, data = quote_ctx.request_history_kline(
                code=futu_code,
                start=start_date,
                end=end_date,
                ktype=KLType.K_DAY,
                autype=AuType.NONE
            )
            
            if ret != 0:
                print(f"  Futu API错误 {ret}: {data}")
                failed += 1
                continue
            
            if data is None or data.empty:
                print(f"  无K线数据")
                continue
            
            print(f"  获取到 {len(data)} 条K线")
            
            cur2 = conn.cursor()
            inserted = 0
            
            for _, row in data.iterrows():
                try:
                    trade_date = row['date'].date() if hasattr(row['date'], 'date') else row['date']
                    
                    op = float(row['open'])
                    cp = float(row['close'])
                    hp = float(row['high'])
                    lp = float(row['low'])
                    vol = int(row['volume']) if row['volume'] else 0
                    tov = float(row['turnover']) if row['turnover'] else 0
                    chg = 0.0  # Futu日K不直接提供涨跌幅，计算麻烦，留0
                    
                    cur2.execute("""
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
                            turnover = EXCLUDED.turnover
                    """, (code, trade_date, op, cp, hp, lp, vol, tov, chg))
                    inserted += 1
                    
                except Exception as e:
                    pass
            
            conn.commit()
            cur2.close()
            
            if inserted > 0:
                print(f"  插入 {inserted} 条K线")
            success += 1
            
        except Exception as e:
            print(f"  失败: {e}")
            failed += 1
            continue
    
    quote_ctx.close()
    conn.close()
    print(f"\n=== 完成: 成功 {success}, 失败 {failed} ===")


if __name__ == '__main__':
    sync_ipo_klines_futu()
