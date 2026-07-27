import psycopg2
conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute("SELECT MAX(trade_date) FROM stock_kline WHERE period_type = 'D'")
print(f'Latest daily K date: {cur.fetchone()[0]}')
cur.execute("SELECT COUNT(*) FROM stock_kline WHERE period_type = 'D'")
print(f'Total daily K records: {cur.fetchone()[0]}')
conn.close()
