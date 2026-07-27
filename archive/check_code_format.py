import psycopg2

conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check stock code format
cur.execute("SELECT stock_code, stock_name FROM stock_ipo WHERE listing_date = '2026-03-30'")
for row in cur.fetchall():
    print(f'  stock_code={repr(row[0])} name={row[1]}')

# Try matching with different formats
for code in ['06636', 'HK.06636', 'HK06636', 'hk.06636']:
    cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE stock_code = %s", (code,))
    count = cur.fetchone()[0]
    print(f'  Matching {repr(code)}: {count} records')

conn.close()
