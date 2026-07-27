import psycopg2

# The 4 IPOs from AASTOCKS sidebar (matched with Futu names)
ipo_data = [
    ('06636', '极视角', 4590.4, 10.0, 40.0),     # issue_price from AASTOCKS
    ('01021', '华沿机器人', 5058.4, 5.0, 17.0),
    ('02726', '瀚天天成', 49.7, 20.0, 76.26),
    ('02526', '德适-B', 1072.4, 3.0, 99.0),
]

# Calculate entry fees: issue_price * lot_size
# 极视角: 40 * 50 = 2000
# 华沿机器人: 17 * 200 = 3400
# 瀚天天成: 76.26 * 50 = 3813
# 德适-B: 99 * 50 = 4950

lot_sizes = {
    '06636': 50,
    '01021': 200,
    '02726': 50,
    '02526': 50,
}

conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

for code, name, ratio, rate, issue_price in ipo_data:
    lot = lot_sizes[code]
    entry_fee = issue_price * lot
    
    cur.execute("""
        UPDATE stock_ipo 
        SET allotment_rate = %s, 
            oversubscription_ratio = %s, 
            issue_price = %s,
            entry_fee = %s
        WHERE stock_code = %s
    """, (rate, ratio, issue_price, entry_fee, code))
    
    print(f'{code} {name}: rate={rate}%, ratio={ratio}x, price={issue_price}, entry={entry_fee} -> {cur.rowcount} rows updated')

conn.commit()

# Verify
print('\n=== Verification ===')
cur.execute("""
    SELECT stock_code, stock_name, listing_date, allotment_rate, oversubscription_ratio, entry_fee, issue_price
    FROM stock_ipo 
    WHERE allotment_rate IS NOT NULL
    ORDER BY listing_date DESC
""")
for row in cur.fetchall():
    print(f'  {row[0]} {row[1]} ({row[2]}): 一手中签率={row[3]}%, 认购倍数={row[4]}x, 入场费={row[5]}, 发行价={row[6]}')

conn.close()
print('\nDone!')
