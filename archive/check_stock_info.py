import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check stock_info for these codes
codes = ['02933', '02926', '02938', '01879', '02493', '03296', '08595']
for code in codes:
    cur.execute("SELECT stock_code, stock_name, listing_date FROM stock_info WHERE stock_code = %s OR stock_code = %s OR stock_code = %s", (code, code.zfill(5), '00' + code))
    rows = cur.fetchall()
    print(f"{code}: {rows}")

# Also check stock_ipo
print("\nstock_ipo:")
for code in codes:
    cur.execute("SELECT stock_code, stock_name, issue_price, listing_date FROM stock_ipo WHERE stock_code = %s OR stock_code = %s", (code, code.zfill(5)))
    rows = cur.fetchall()
    print(f"{code}: {rows}")