"""
用 akshare 获取港股月K/年K数据，写入数据库
列顺序: 0=日期, 1=开盘, 2=收盘, 3=最高, 4=最低, 5=成交量, 6=成交额, 7=振幅, 8=涨跌幅, 9=涨跌额, 10=换手率
"""
import psycopg2
import akshare as ak
import pandas as pd
from datetime import datetime

DB_CONFIG = {
    "host": "localhost", "port": 5432, "dbname": "hk_stock",
    "user": "postgres", "password": "pc20050218"
}

def fetch_and_save(stock_code, period="monthly"):
    code = stock_code  # akshare 需要完整代码如 01810
    
    try:
        df = ak.stock_hk_hist(
            symbol=code,
            period=period,
            start_date="20150101",
            end_date=datetime.now().strftime("%Y%m%d"),
            adjust=""
        )
        
        if df.empty:
            print(f"  {stock_code} ({period}): 无数据")
            return 0
        
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        
        period_type = "M" if period == "monthly" else ("Y" if period == "yearly" else "W")
        count = 0
        
        for _, row in df.iterrows():
            trade_date = row.iloc[0]  # 日期
            open_p = float(row.iloc[1])
            close_p = float(row.iloc[2])
            high_p = float(row.iloc[3])
            low_p = float(row.iloc[4])
            volume = int(row.iloc[5])
            turnover = float(row.iloc[6])
            chg_pct = float(row.iloc[8])  # 涨跌幅
            
            cur.execute(
                "SELECT id FROM stock_kline WHERE stock_code=%s AND period_type=%s AND trade_date=%s",
                (stock_code, period_type, trade_date)
            )
            
            if cur.fetchone():
                cur.execute("""
                    UPDATE stock_kline SET open_price=%s, close_price=%s, high_price=%s, low_price=%s,
                        volume=%s, turnover=%s, change_percent=%s
                    WHERE stock_code=%s AND period_type=%s AND trade_date=%s
                """, (open_p, close_p, high_p, low_p, volume, turnover, chg_pct, stock_code, period_type, trade_date))
            else:
                cur.execute("""
                    INSERT INTO stock_kline (stock_code, period_type, trade_date, open_price, close_price,
                        high_price, low_price, volume, turnover, change_percent, turnover_rate)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                """, (stock_code, period_type, trade_date, open_p, close_p, high_p, low_p, volume, turnover, chg_pct))
            count += 1
        
        conn.commit()
        cur.close()
        conn.close()
        print(f"  {stock_code} ({period}): {count} 条")
        return count
        
    except Exception as e:
        print(f"  {stock_code} ({period}): 失败 - {e}")
        import traceback; traceback.print_exc()
        return 0

def main():
    import sys
    code = sys.argv[1] if len(sys.argv) > 1 else "01810"
    
    print(f"获取 {code} 月K数据...")
    fetch_and_save(code, "monthly")
    
    # 年K需要从月K手动聚合
    print(f"从月K聚合年K...")
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute("""
        SELECT trade_date, open_price, close_price, high_price, low_price, volume, turnover
        FROM stock_kline WHERE stock_code=%s AND period_type='M' ORDER BY trade_date
    """, (code,))
    monthly_data = cur.fetchall()
    
    from collections import defaultdict
    yearly = defaultdict(list)
    for r in monthly_data:
        yearly[r[0].strftime("%Y")].append(r)
    
    ycount = 0
    for yk, rows in sorted(yearly.items()):
        td = rows[-1][0]
        op = rows[0][1]; cp = rows[-1][2]
        hp = max(r[3] for r in rows); lp = min(r[4] for r in rows)
        vol = sum(r[5] or 0 for r in rows)
        tov = sum(float(r[6] or 0) for r in rows)
        chg = ((float(cp)/float(op))-1)*100 if op and cp else 0
        
        cur.execute("SELECT id FROM stock_kline WHERE stock_code=%s AND period_type='Y' AND trade_date=%s", (code, td))
        if cur.fetchone():
            cur.execute("UPDATE stock_kline SET open_price=%s,close_price=%s,high_price=%s,low_price=%s,volume=%s,turnover=%s,change_percent=%s WHERE stock_code=%s AND period_type='Y' AND trade_date=%s",
                (op,cp,hp,lp,vol,tov,round(chg,4),code,td))
        else:
            cur.execute("INSERT INTO stock_kline (stock_code,period_type,trade_date,open_price,close_price,high_price,low_price,volume,turnover,change_percent,turnover_rate) VALUES (%s,'Y',%s,%s,%s,%s,%s,%s,%s,%s,0)",
                (code,td,op,cp,hp,lp,vol,tov,round(chg,4)))
        ycount += 1
    
    conn.commit()
    print(f"  {code} 年K: {ycount} 条")
    
    cur.execute("SELECT period_type, COUNT(*) FROM stock_kline WHERE stock_code=%s GROUP BY period_type", (code,))
    print(f"\n{code} 数据统计:")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]} 条")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
