import psycopg2
conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute("SELECT config_key, config_value FROM stock_config")
for row in cur.fetchall():
    val = row[1]
    if row[0] == 'ai_api_key':
        print(f'{row[0]}: {repr(val)} (len={len(val)})')
    else:
        print(f'{row[0]}: {val}')
conn.close()
