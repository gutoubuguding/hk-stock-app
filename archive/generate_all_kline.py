"""
批量从日K数据计算月K和年K
"""
import psycopg2
from collections import defaultdict

DB_CONFIG = {
    "host": "localhost", "port": 5432, "dbname": "hk_stock",
    "user": "postgres", "password": "pc20050218"
}

def process_all():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute("SELECT DISTINCT stock_code FROM stock_kline WHERE period_type='D'")
    codes = [r[0] for r in cur.fetchall()]
    print(f"共 {len(codes)} 只股票需要处理")
    
    for i, code in enumerate(codes):
        cur.execute("""
            SELECT trade_date, open_price, close_price, high_price, low_price,
                   volume, turnover
            FROM stock_kline WHERE stock_code=%s AND period_type='D' ORDER BY trade_date
        """, (code,))
        daily = cur.fetchall()
        if not daily:
            continue
        
        # 月K
        monthly = defaultdict(list)
        for r in daily:
            monthly[r[0].strftime("%Y-%m")].append(r)
        
        for mk, rows in sorted(monthly.items()):
            td = rows[-1][0]
            op = rows[0][1]; cp = rows[-1][2]
            hp = max((r[3] for r in rows if r[3] is not None), default=0)
            lp = min((r[4] for r in rows if r[4] is not None), default=0)
            vol = sum(r[5] or 0 for r in rows)
            tov = sum(float(r[6] or 0) for r in rows)
            chg = ((float(cp)/float(op))-1)*100 if op and cp else 0
            
            cur.execute("SELECT id FROM stock_kline WHERE stock_code=%s AND period_type='M' AND trade_date=%s", (code, td))
            if cur.fetchone():
                cur.execute("UPDATE stock_kline SET open_price=%s,close_price=%s,high_price=%s,low_price=%s,volume=%s,turnover=%s,change_percent=%s WHERE stock_code=%s AND period_type='M' AND trade_date=%s",
                    (op,cp,hp,lp,vol,tov,round(chg,4),code,td))
            else:
                cur.execute("INSERT INTO stock_kline (stock_code,period_type,trade_date,open_price,close_price,high_price,low_price,volume,turnover,change_percent,turnover_rate) VALUES (%s,'M',%s,%s,%s,%s,%s,%s,%s,%s,0)",
                    (code,td,op,cp,hp,lp,vol,tov,round(chg,4)))
        
        # 年K
        yearly = defaultdict(list)
        for r in daily:
            yearly[r[0].strftime("%Y")].append(r)
        
        for yk, rows in sorted(yearly.items()):
            td = rows[-1][0]
            op = rows[0][1]; cp = rows[-1][2]
            hp = max((r[3] for r in rows if r[3] is not None), default=0)
            lp = min((r[4] for r in rows if r[4] is not None), default=0)
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
        
        if (i+1) % 50 == 0:
            conn.commit()
            print(f"已处理 {i+1}/{len(codes)}")
    
    conn.commit()
    cur.close()
    conn.close()
    print(f"全部完成! 共处理 {len(codes)} 只股票")

if __name__ == "__main__":
    process_all()
