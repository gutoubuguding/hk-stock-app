import psycopg2

conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check IPO table schema
cur.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'stock_ipo' 
    ORDER BY ordinal_position
""")
print('=== IPO Table Schema ===')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]}')

# Check current IPO data count
cur.execute('SELECT COUNT(*) FROM stock_ipo')
print(f'\n=== Total IPO records: {cur.fetchone()[0]} ===')

# Show sample data with all fields
cur.execute('SELECT * FROM stock_ipo ORDER BY listing_date DESC LIMIT 5')
cols = [desc[0] for desc in cur.description]
print(f'\nColumns: {cols}')
for row in cur.fetchall():
    print(row)

# Check if there's any success rate data
cur.execute("""
    SELECT column_name FROM information_schema.columns 
    WHERE table_name = 'stock_ipo' AND column_name LIKE '%rate%' OR column_name LIKE '%success%' OR column_name LIKE '%winning%'
""")
print('\n=== Success rate columns: ===')
for row in cur.fetchall():
    print(f'  {row[0]}')

conn.close()
