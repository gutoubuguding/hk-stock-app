"""
从日K数据计算月K和年K，写入数据库
"""
import psycopg2
from collections import defaultdict
from decimal import Decimal

DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "dbname": "hk_stock",
    "user": "postgres",
    "password": "pc20050218"
}

def aggregate_kline(stock_code):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 读取日K数据
    cur.execute("""
        SELECT trade_date, open_price, close_price, high_price, low_price, 
               volume, turnover, change_percent, turnover_rate
        FROM stock_kline 
        WHERE stock_code = %s AND period_type = 'D'
        ORDER BY trade_date
    """, (stock_code,))
    daily_data = cur.fetchall()
    
    if not daily_data:
        print(f"没有找到 {stock_code} 的日K数据")
        return
    
    print(f"读取到 {len(daily_data)} 条日K数据")
    
    # === 月K ===
    monthly = defaultdict(list)
    for row in daily_data:
        key = row[0].strftime("%Y-%m")
        monthly[key].append(row)
    
    monthly_count = 0
    for month_key, rows in sorted(monthly.items()):
        trade_date = rows[-1][0]  # 用该月最后一天
        open_price = rows[0][1]   # 月初开盘
        close_price = rows[-1][2]  # 月末收盘
        high_price = max(r[3] for r in rows)
        low_price = min(r[4] for r in rows)
        volume = sum(r[5] or 0 for r in rows)
        turnover = sum(float(r[6] or 0) for r in rows)
        change_pct = ((float(close_price) / float(rows[0][1])) - 1) * 100 if rows[0][1] else 0
        
        # 检查是否已存在
        cur.execute("""
            SELECT id FROM stock_kline 
            WHERE stock_code = %s AND period_type = 'M' AND trade_date = %s
        """, (stock_code, trade_date))
        
        if cur.fetchone():
            cur.execute("""
                UPDATE stock_kline SET 
                    open_price=%s, close_price=%s, high_price=%s, low_price=%s,
                    volume=%s, turnover=%s, change_percent=%s
                WHERE stock_code=%s AND period_type='M' AND trade_date=%s
            """, (open_price, close_price, high_price, low_price, 
                  volume, turnover, round(change_pct, 4), stock_code, trade_date))
        else:
            cur.execute("""
                INSERT INTO stock_kline (stock_code, period_type, trade_date, 
                    open_price, close_price, high_price, low_price,
                    volume, turnover, change_percent, turnover_rate)
                VALUES (%s, 'M', %s, %s, %s, %s, %s, %s, %s, %s, 0)
            """, (stock_code, trade_date, open_price, close_price, high_price, low_price,
                  volume, turnover, round(change_pct, 4)))
        monthly_count += 1
    
    print(f"写入 {monthly_count} 条月K数据")
    
    # === 年K ===
    yearly = defaultdict(list)
    for row in daily_data:
        key = row[0].strftime("%Y")
        yearly[key].append(row)
    
    yearly_count = 0
    for year_key, rows in sorted(yearly.items()):
        trade_date = rows[-1][0]
        open_price = rows[0][1]
        close_price = rows[-1][2]
        high_price = max(r[3] for r in rows)
        low_price = min(r[4] for r in rows)
        volume = sum(r[5] or 0 for r in rows)
        turnover = sum(float(r[6] or 0) for r in rows)
        change_pct = ((float(close_price) / float(rows[0][1])) - 1) * 100 if rows[0][1] else 0
        
        cur.execute("""
            SELECT id FROM stock_kline 
            WHERE stock_code = %s AND period_type = 'Y' AND trade_date = %s
        """, (stock_code, trade_date))
        
        if cur.fetchone():
            cur.execute("""
                UPDATE stock_kline SET 
                    open_price=%s, close_price=%s, high_price=%s, low_price=%s,
                    volume=%s, turnover=%s, change_percent=%s
                WHERE stock_code=%s AND period_type='Y' AND trade_date=%s
            """, (open_price, close_price, high_price, low_price,
                  volume, turnover, round(change_pct, 4), stock_code, trade_date))
        else:
            cur.execute("""
                INSERT INTO stock_kline (stock_code, period_type, trade_date,
                    open_price, close_price, high_price, low_price,
                    volume, turnover, change_percent, turnover_rate)
                VALUES (%s, 'Y', %s, %s, %s, %s, %s, %s, %s, %s, 0)
            """, (stock_code, trade_date, open_price, close_price, high_price, low_price,
                  volume, turnover, round(change_pct, 4)))
        yearly_count += 1
    
    print(f"写入 {yearly_count} 条年K数据")
    
    conn.commit()
    cur.close()
    conn.close()
    print("完成!")

if __name__ == "__main__":
    import sys
    code = sys.argv[1] if len(sys.argv) > 1 else "01810"
    aggregate_kline(code)
