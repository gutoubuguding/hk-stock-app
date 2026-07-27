"""批量同步港股K线 - 健壮版"""
import sys; sys.stdout.reconfigure(line_buffering=True)
import psycopg2, akshare as ak, time, traceback
from collections import defaultdict

DB = {"host":"localhost","port":5432,"dbname":"hk_stock","user":"postgres","password":"pc20050218"}

def upsert(cur, code, pt, td, op, cp, hp, lp, vol, tov, chg):
    cur.execute("SELECT id FROM stock_kline WHERE stock_code=%s AND period_type=%s AND trade_date=%s",(code,pt,td))
    if cur.fetchone():
        cur.execute("UPDATE stock_kline SET open_price=%s,close_price=%s,high_price=%s,low_price=%s,volume=%s,turnover=%s,change_percent=%s WHERE stock_code=%s AND period_type=%s AND trade_date=%s",(op,cp,hp,lp,vol,tov,chg,code,pt,td))
    else:
        cur.execute("INSERT INTO stock_kline (stock_code,period_type,trade_date,open_price,close_price,high_price,low_price,volume,turnover,change_percent,turnover_rate) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0)",(code,pt,td,op,cp,hp,lp,vol,tov,chg))

def sync_one(code):
    conn = psycopg2.connect(**DB)
    cur = conn.cursor()
    try:
        for period, pt in [("daily","D"),("monthly","M")]:
            df = ak.stock_hk_hist(symbol=code, period=period, start_date="20150101", end_date="20260330", adjust="")
            for _, r in df.iterrows():
                upsert(cur, code, pt, r.iloc[0], float(r.iloc[1]), float(r.iloc[2]),
                    float(r.iloc[3]), float(r.iloc[4]), int(r.iloc[5]), float(r.iloc[6]), float(r.iloc[8]))
        
        # 年K
        cur.execute("SELECT trade_date,open_price,close_price,high_price,low_price,volume,turnover FROM stock_kline WHERE stock_code=%s AND period_type='M' ORDER BY trade_date",(code,))
        m = cur.fetchall(); yd = defaultdict(list)
        for r in m: yd[r[0].strftime("%Y")].append(r)
        for yk,rows in sorted(yd.items()):
            td=rows[-1][0];op=rows[0][1];cp=rows[-1][2]
            upsert(cur,code,"Y",td,op,cp,max(r[3]for r in rows),min(r[4]for r in rows),sum(r[5]or 0 for r in rows),sum(float(r[6]or 0)for r in rows),round(((float(cp)/float(op))-1)*100,4)if op and cp else 0)
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        return False
    finally:
        cur.close(); conn.close()

# 主流程
conn = psycopg2.connect(**DB); c = conn.cursor()
c.execute("SELECT stock_code FROM stock_info ORDER BY stock_code")
all_codes = [r[0] for r in c.fetchall()]
c.execute("SELECT DISTINCT stock_code FROM stock_kline WHERE period_type='D'")
done = set(r[0] for r in c.fetchall())
c.close(); conn.close()

todo = [x for x in all_codes if x not in done]
print(f"总计{len(all_codes)}只, 已完成{len(done)}只, 待同步{len(todo)}只", flush=True)

ok=fail=0
for i,code in enumerate(todo):
    if sync_one(code): ok+=1
    else: fail+=1
    if(i+1)%50==0: print(f"  {i+1}/{len(todo)} ok={ok} fail={fail}",flush=True)

print(f"\n完成! 成功{ok} 失败{fail}", flush=True)

conn=psycopg2.connect(**DB);c=conn.cursor()
c.execute("SELECT period_type,COUNT(*),COUNT(DISTINCT stock_code) FROM stock_kline GROUP BY period_type")
for r in c.fetchall(): print(f"  {r[0]}: {r[1]}条/{r[2]}只",flush=True)
c.close();conn.close()
