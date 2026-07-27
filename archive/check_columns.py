import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute('SELECT column_name FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position', ('stock_ipo',))
for row in cur.fetchall():
    print(row[0])