import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

cur.execute('SELECT COUNT(*) FROM stock_info')
print('stock_info count:', cur.fetchone()[0])

cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01'")
print('stock_ipo count:', cur.fetchone()[0])

cur.execute('SELECT COUNT(*) FROM stock_kline')
print('stock_kline count:', cur.fetchone()[0])

cur.execute('SELECT COUNT(*) FROM news')
print('news count:', cur.fetchone()[0])