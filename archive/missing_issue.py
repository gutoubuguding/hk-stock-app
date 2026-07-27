import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute("SELECT stock_code, stock_name, listing_date FROM stock_ipo WHERE listing_date >= '2025-01-01' AND issue_price IS NULL ORDER BY listing_date")
for row in cur.fetchall():
    print(row[0], row[1], row[2])