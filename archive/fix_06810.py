import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# 06810 is a future listing (2026-04-29), first_day_change = 100 is placeholder
cur.execute("UPDATE stock_ipo SET first_day_change = NULL, updated_at = NOW() WHERE stock_code = '06810'")
conn.commit()
print("06810 fixed")