import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check 08595 - 0.01 as issue_price seems wrong
# Check what the correct issue_price might be
cur.execute("SELECT stock_code, stock_name, issue_price FROM stock_ipo WHERE stock_code IN ('08595', '02938', '02933', '02926', '03296', '02493', '01879')")
for row in cur.fetchall():
    print(f"{row[0]} {row[1]}: issue={row[2]}")