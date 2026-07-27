import psycopg2

conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Top HK stocks
codes = ['00700','09988','03690','01810','00005','01299','02318','00941','03988','02020','01211','09618']
print("=== Top 港股通股票K线状态 ===")
for code in codes:
    cur.execute("""
        SELECT trade_date, close_price FROM stock_kline
        WHERE stock_code = %s AND period_type = 'D'
        ORDER BY trade_date DESC LIMIT 3
    """, (code,))
    rows = cur.fetchall()
    if rows:
        dates = [str(r[0]) for r in rows]
        prices = [r[1] for r in rows]
        print(f'{code}: 最新 {dates[0]} 收盘{prices[0]}')
    else:
        print(f'{code}: 无数据')

# Count total
cur.execute("SELECT COUNT(DISTINCT stock_code) FROM stock_kline WHERE period_type = 'D'")
print(f"\n共有 {cur.fetchone()[0]} 只股票有K线数据")

cur.close(); conn.close()