import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

cur.execute("SELECT * FROM stock_config")
rows = cur.fetchall()
print("stock_config table:")
for row in rows:
    print(f"  {row}")