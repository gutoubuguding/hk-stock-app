import psycopg2
import akshare as ak
from datetime import datetime

conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check which stocks have data for 3/27 and 3/30
cur.execute("""
    SELECT trade_date, COUNT(*) as cnt
    FROM stock_kline 
    WHERE period_type = 'D' AND trade_date >= '2026-03-27'
    GROUP BY trade_date
    ORDER BY trade_date
""")
print('=== 3/27以来每日K线记录数 ===')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]} 条')

# Check if 09988 has 3/27 data
cur.execute("SELECT * FROM stock_kline WHERE stock_code = '09988' AND period_type = 'D' AND trade_date = '2026-03-27'")
print(f'\n09988 3/27数据: {"有" if cur.fetchone() else "无"}')

# Try to sync 09988 specifically
print('\n=== 尝试同步09988最新数据 ===')
try:
    df = ak.stock_hk_hist(symbol='09988', period="daily", start_date="20260325", end_date="20260330", adjust="")
    print(f'akshare返回 {len(df)} 条记录:')
    for _, row in df.iterrows():
        print(f'  {row.iloc[0]}: open={row.iloc[1]}, close={row.iloc[2]}, high={row.iloc[3]}, low={row.iloc[4]}')
        
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
            (stock_code, period_type, trade_date, open_price, close_price, high_price, low_price, volume, turnover, change_percent, turnover_rate)
            VALUES (%s, 'D', %s, %s, %s, %s, %s, %s, %s, %s, 0)
            ON CONFLICT DO NOTHING
        """, ('09988', td, op, cp, hp, lp, vol, tov, chg))
    
    conn.commit()
    print('数据库已更新')
except Exception as e:
    print(f'Error: {e}')

conn.close()
