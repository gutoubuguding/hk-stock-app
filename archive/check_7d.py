import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01' AND seven_day_change IS NOT NULL")
print('有seven_day_change的:', cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01' AND thirty_day_change IS NOT NULL")
print('有thirty_day_change的:', cur.fetchone()[0])
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01' AND current_change IS NOT NULL")
print('有current_change的:', cur.fetchone()[0])