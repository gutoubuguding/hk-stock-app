import psycopg2
conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute("UPDATE stock_config SET config_value = '' WHERE config_key = 'ai_api_key'")
conn.commit()
cur.execute("SELECT config_key, config_value FROM stock_config")
for row in cur.fetchall():
    print(f'{row[0]}: {repr(row[1])}')
conn.close()
