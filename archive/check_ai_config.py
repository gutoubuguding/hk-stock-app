import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check the config table
cur.execute('SELECT * FROM app_config LIMIT 5')
rows = cur.fetchall()
print("app_config table:")
for row in rows:
    print(f"  {row}")

# Check if there's an ai_api_key
cur.execute("SELECT config_key, config_value FROM app_config WHERE config_key LIKE '%ai%'")
rows = cur.fetchall()
print("\nAI config:")
for row in rows:
    key = row[0] if len(row) > 0 else ''
    val = row[1] if len(row) > 1 else ''
    # Mask the API key
    if 'key' in key.lower():
        val = val[:10] + '***' if val else 'EMPTY'
    print(f"  {key}: {val}")