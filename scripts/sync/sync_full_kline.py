"""
用 akshare 为所有港股同步日K+月K+年K
"""
import psycopg2
import akshare as ak
import time
from collections import defaultdict

DB_CONFIG = {
    "host": "localhost", "port": 5432, "dbname": "hk_stock",
    "user": "postgres", "password": "pc20050218"
}

def upsert_kline(cur, code, period_type, td, op, cp, hp, lp, vol, tov, chg):
    cur.execute("SELECT id FROM stock_kline WHERE stock_code=%s AND period_type=%s AND trade_date=%s", (code, period_type, td))
    if cur.fetchone():
        cur.execute("UPDATE stock_kline SET open_price=%s,close_price=%s,high_price=%s,low_price=%s,volume=%s,turnover=%s,change_percent=%s WHERE stock_code=%s AND period_type=%s AND trade_date=%s",
            (op,cp,hp,lp,vol,tov,chg,code,period_type,td))
    else:
        cur.execute("INSERT INTO stock_kline (stock_code,period_type,trade_date,open_price,close_price,high_price,low_price,volume,turnover,change_percent,turnover_rate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0)",
            (code,period_type,td,op,cp,hp,lp,vol,tov,chg))

def sync_stock(code, conn):
    cur = conn.cursor()
    
    # 日K
    try:
        df = ak.stock_hk_hist(symbol=code, period="daily", start_date="20240101", end_date="20260330", adjust="")
        for _, row in df.iterrows():
            upsert_kline(cur, code, "D", row.iloc[0], float(row.iloc[1]), float(row.iloc[2]),
                float(row.iloc[3]), float(row.iloc[4]), int(row.iloc[5]), float(row.iloc[6]), float(row.iloc[8]))
    except:
        pass
    
    # 月K
    try:
        df = ak.stock_hk_hist(symbol=code, period="monthly", start_date="20150101", end_date="20260330", adjust="")
        for _, row in df.iterrows():
            upsert_kline(cur, code, "M", row.iloc[0], float(row.iloc[1]), float(row.iloc[2]),
                float(row.iloc[3]), float(row.iloc[4]), int(row.iloc[5]), float(row.iloc[6]), float(row.iloc[8]))
    except:
        pass
    
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
        upsert_kline(cur, code, "Y", td, op, cp, hp, lp, vol, tov, round(chg,4))
    
    conn.commit()
    cur.close()

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    cur.execute("SELECT stock_code FROM stock_info ORDER BY stock_code")
    codes = [r[0] for r in cur.fetchall()]
    cur.close()
    
    # 跳过已有数据的
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT stock_code FROM stock_kline WHERE period_type='D'")
    existing = set(r[0] for r in cur.fetchall())
    cur.close()
    
    todo = [c for c in codes if c not in existing]
    total = len(todo)
    print(f"共 {len(codes)} 只股票, 已有数据 {len(existing)} 只, 需同步 {total} 只")
    
    ok, fail = 0, 0
    for i, code in enumerate(todo):
        try:
            sync_stock(code, conn)
            ok += 1
        except:
            fail += 1
        
        if (i+1) % 50 == 0:
            print(f"  进度: {i+1}/{total} (成功:{ok} 失败:{fail})")
            time.sleep(0.5)
    
    conn.close()
    print(f"完成! 成功: {ok}, 失败: {fail}")
    
    # 最终统计
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("SELECT period_type, COUNT(*), COUNT(DISTINCT stock_code) FROM stock_kline GROUP BY period_type")
    print("\n最终统计:")
    for r in cur.fetchall():
        print(f"  {r[0]}: {r[1]} 条, 涵盖 {r[2]} 只股票")
    cur.close()
    conn.close()

if __name__ == "__main__":
    main()
