"""
批量用 akshare 同步所有港股月K/年K
"""
import psycopg2
import akshare as ak
import time
from collections import defaultdict

DB_CONFIG = {
    "host": "localhost", "port": 5432, "dbname": "hk_stock",
    "user": "postgres", "password": "pc20050218"
}

def sync_stock(code, conn):
    cur = conn.cursor()
    success = True
    
    # 月K
    try:
        df = ak.stock_hk_hist(symbol=code, period="monthly", start_date="20150101", end_date="20260330", adjust="")
        for _, row in df.iterrows():
            td = row.iloc[0]; op = float(row.iloc[1]); cp = float(row.iloc[2])
            hp = float(row.iloc[3]); lp = float(row.iloc[4])
            vol = int(row.iloc[5]); tov = float(row.iloc[6]); chg = float(row.iloc[8])
            
            cur.execute("SELECT id FROM stock_kline WHERE stock_code=%s AND period_type='M' AND trade_date=%s", (code, td))
            if cur.fetchone():
                cur.execute("UPDATE stock_kline SET open_price=%s,close_price=%s,high_price=%s,low_price=%s,volume=%s,turnover=%s,change_percent=%s WHERE stock_code=%s AND period_type='M' AND trade_date=%s",
                    (op,cp,hp,lp,vol,tov,chg,code,td))
            else:
                cur.execute("INSERT INTO stock_kline (stock_code,period_type,trade_date,open_price,close_price,high_price,low_price,volume,turnover,change_percent,turnover_rate) VALUES (%s,'M',%s,%s,%s,%s,%s,%s,%s,%s,0)",
                    (code,td,op,cp,hp,lp,vol,tov,chg))
    except Exception as e:
        success = False
    
    # 年K (从月K聚合)
    cur.execute("SELECT trade_date, open_price, close_price, high_price, low_price, volume, turnover FROM stock_kline WHERE stock_code=%s AND period_type='M' ORDER BY trade_date", (code,))
    monthly = cur.fetchall()
    yearly = defaultdict(list)
    for r in monthly:
        yearly[r[0].strftime("%Y")].append(r)
    
    for yk, rows in sorted(yearly.items()):
        td = rows[-1][0]; op = rows[0][1]; cp = rows[-1][2]
        hp = max(r[3] for r in rows); lp = min(r[4] for r in rows)
        vol = sum(r[5] or 0 for r in rows); tov = sum(float(r[6] or 0) for r in rows)
        chg = ((float(cp)/float(op))-1)*100 if op and cp else 0
        cur.execute("SELECT id FROM stock_kline WHERE stock_code=%s AND period_type='Y' AND trade_date=%s", (code, td))
        if cur.fetchone():
            cur.execute("UPDATE stock_kline SET open_price=%s,close_price=%s,high_price=%s,low_price=%s,volume=%s,turnover=%s,change_percent=%s WHERE stock_code=%s AND period_type='Y' AND trade_date=%s",
                (op,cp,hp,lp,vol,tov,round(chg,4),code,td))
        else:
            cur.execute("INSERT INTO stock_kline (stock_code,period_type,trade_date,open_price,close_price,high_price,low_price,volume,turnover,change_percent,turnover_rate) VALUES (%s,'Y',%s,%s,%s,%s,%s,%s,%s,%s,0)",
                (code,td,op,cp,hp,lp,vol,tov,round(chg,4)))
    
    conn.commit()
    cur.close()
    return success, len(monthly), len(yearly)

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # 只同步有日K数据但月K不足的股票
    cur.execute("""
        SELECT DISTINCT d.stock_code FROM stock_kline d 
        WHERE d.period_type='D' AND d.stock_code NOT IN (
            SELECT stock_code FROM stock_kline WHERE period_type='M' GROUP BY stock_code HAVING COUNT(*) > 12
        )
    """)
    codes = [r[0] for r in cur.fetchall()]
    cur.close()
    
    print(f"需要同步 {len(codes)} 只股票")
    
    ok, fail = 0, 0
    for i, code in enumerate(codes):
        try:
            s, mc, yc = sync_stock(code, conn)
            if s:
                ok += 1
            else:
                fail += 1
        except Exception as e:
            fail += 1
        
        if (i+1) % 20 == 0:
            print(f"  进度: {i+1}/{len(codes)} (成功:{ok} 失败:{fail})")
            time.sleep(1)  # 避免请求过快
    
    conn.close()
    print(f"完成! 成功: {ok}, 失败: {fail}, 总计: {len(codes)}")

if __name__ == "__main__":
    main()
