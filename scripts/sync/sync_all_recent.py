import psycopg2
import akshare as ak
import time
from datetime import datetime, date

DB_CONFIG = {
    "host": "localhost", "port": 5432, "dbname": "hk_stock",
    "user": "postgres", "password": "pc20050218"
}

def sync_stock(code, conn):
    """Sync latest daily K data for a stock"""
    cur = conn.cursor()
    
    try:
        df = ak.stock_hk_hist(symbol=code, period="daily", start_date="20260320", end_date="20260330", adjust="")
        count = 0
        for _, row in df.iterrows():
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
            """, (code, td, op, cp, hp, lp, vol, tov, chg))
            if cur.rowcount > 0:
                count += 1
        
        conn.commit()
        cur.close()
        return True, count
    except Exception as e:
        conn.rollback()
        cur.close()
        return False, str(e)

def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Get all stocks that have daily K data
    cur.execute("""
        SELECT DISTINCT stock_code 
        FROM stock_kline 
        WHERE period_type = 'D'
        ORDER BY stock_code
    """)
    codes = [r[0] for r in cur.fetchall()]
    cur.close()
    
    print(f'需要同步 {len(codes)} 只股票')
    
    ok = 0
    fail = 0
    total_new = 0
    
    for i, code in enumerate(codes):
        success, result = sync_stock(code, conn)
        if success:
            ok += 1
            total_new += result
        else:
            fail += 1
            if fail <= 3:
                print(f'  {code} 失败: {result}')
        
        if (i + 1) % 100 == 0:
            print(f'  进度: {i+1}/{len(codes)} (成功:{ok} 失败:{fail} 新增:{total_new}条)')
            time.sleep(2)
    
    conn.close()
    print(f'\n完成! 成功: {ok}, 失败: {fail}, 新增K线: {total_new}条')

if __name__ == '__main__':
    main()
