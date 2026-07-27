import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check stock_ipo for missing issue_price stocks
codes = ['02933', '02926', '02938', '01879', '02493', '03296', '08595']
print("stock_ipo:")
for code in codes:
    cur.execute("SELECT stock_code, stock_name, issue_price, listing_date FROM stock_ipo WHERE stock_code = %s", (code,))
    rows = cur.fetchall()
    for row in rows:
        print(f"  {row[0]} {row[1]}: issue={row[2]}, listing={row[3]}")