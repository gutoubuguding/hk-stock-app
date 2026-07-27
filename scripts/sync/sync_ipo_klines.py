#!/usr/bin/env python3
"""
补全新股K线数据
针对在 stock_ipo 表里但不在 stock_info 表里、或K线数据缺失的股票
"""
import os
os.environ['NO_PROXY'] = '*'

import akshare as ak
import psycopg2
from datetime import datetime, date
import time

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "database": "hk_stock",
    "user": "postgres",
    "password": "pc20050218"
}


def sync_ipo_klines():
    """补全新股的K线数据"""
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 找出所有K线数据缺失的股票（在stock_info里但没有D K线）
    cur.execute("""
        SELECT DISTINCT si.stock_code, si.stock_name
        FROM stock_info si
        LEFT JOIN stock_kline sk ON si.stock_code = sk.stock_code AND sk.period_type = 'D'
        WHERE sk.stock_code IS NULL
    """)
    missing_stocks = cur.fetchall()
    
    print(f"发现 {len(missing_stocks)} 只股票缺少日K线数据")
    
    if not missing_stocks:
        print("没有缺失K线的股票")
        cur.close()
        conn.close()
        return
    
    # 也检查stock_ipo里不在stock_info里的股票
    cur.execute("""
        SELECT i.stock_code, i.stock_name, i.listing_date
        FROM stock_ipo i
        LEFT JOIN stock_info s ON i.stock_code = s.stock_code
        LEFT JOIN stock_kline sk ON i.stock_code = sk.stock_code AND sk.period_type = 'D'
        WHERE s.stock_code IS NULL OR sk.stock_code IS NULL
        ORDER BY i.listing_date DESC
    """)
    ipo_missing = cur.fetchall()
    print(f"IPO相关缺失股票: {len(ipo_missing)} 只")
    
    all_missing = {r[0]: r for r in missing_stocks}
    for r in ipo_missing:
        all_missing[r[0]] = r
    
    print(f"\n开始补全 {len(all_missing)} 只股票的K线数据...")
    
    success = 0
    failed = 0
    
    for code, info in all_missing.items():
        name = info[1] if info else code
        print(f"\n处理: {code} {name}")
        
        try:
            # 用akshare获取日K数据，最多取2年（足够覆盖刚上市的新股）
            end_date = datetime.now().strftime('%Y%m%d')
            start_date = (date.today().replace(year=date.today().year - 2)).strftime('%Y%m%d')
            
            df = ak.stock_hk_hist(
                symbol=code,
                period="daily",
                start_date=start_date,
                end_date=end_date,
                adjust=""
            )
            
            if df is None or df.empty:
                print(f"  {code}: akshare无数据")
                failed += 1
                continue
            
            print(f"  获取到 {len(df)} 条K线数据")
            
            inserted = 0
            for _, row in df.iterrows():
                try:
                    td = row.iloc[0]
                    if isinstance(td, str):
                        td = datetime.strptime(td[:10], '%Y-%m-%d').date()
                    
                    op = float(row.iloc[1])
                    cp = float(row.iloc[2])
                    hp = float(row.iloc[3])
                    lp = float(row.iloc[4])
                    vol = int(row.iloc[5])
                    tov = float(row.iloc[6])
                    chg = float(row.iloc[8]) if len(row) > 8 else 0
                    
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
                    """, (code, td, op, cp, hp, lp, vol, tov, chg))
                    inserted += 1
                    
                except Exception as e:
                    print(f"  插入K线失败: {e}")
                    continue
            
            conn.commit()
            print(f"  {code}: 插入/更新 {inserted} 条K线")
            success += 1
            
            # 避免请求过快
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  {code} 获取数据失败: {e}")
            failed += 1
            continue
    
    cur.close()
    conn.close()
    print(f"\n=== 完成 ===")
    print(f"成功: {success}, 失败: {failed}")


if __name__ == '__main__':
    sync_ipo_klines()
