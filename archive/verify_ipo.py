import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute("""
    SELECT stock_code, stock_name, listing_date, issue_price, sector, 
           subscription_start, lot_size, sponsor,
           oversubscription_ratio, allotment_rate, first_day_change
    FROM stock_ipo 
    WHERE stock_code IN ('00664', '03625', '06636', '01021', '02526')
    ORDER BY stock_code
""")
for row in cur.fetchall():
    print(f'{row[0]} | {row[1]} | 上市:{row[2]} | 发行价:{row[3]} | 行业:{row[4]}')
    print(f'  招股:{row[5]} | 每手:{row[6]} | 保荐:{str(row[7])[:30] if row[7] else None}')
    print(f'  超购:{row[8]} | 中签:{row[9]}% | 首日涨跌:{row[10]}%')
    print()