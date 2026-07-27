import psycopg2

conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Create config table
cur.execute("""
    CREATE TABLE IF NOT EXISTS stock_config (
        id SERIAL PRIMARY KEY,
        config_key VARCHAR(100) UNIQUE NOT NULL,
        config_value TEXT,
        description VARCHAR(255),
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
""")
print('Created stock_config table')

# Insert default config values
defaults = [
    ('ai_provider', 'openai', 'AI服务提供商'),
    ('ai_model', 'gpt-4', 'AI模型名称'),
    ('ai_api_key', '', 'AI API密钥'),
    ('ai_base_url', 'https://api.openai.com/v1', 'AI API地址'),
]

for key, value, desc in defaults:
    cur.execute("""
        INSERT INTO stock_config (config_key, config_value, description)
        VALUES (%s, %s, %s)
        ON CONFLICT (config_key) DO NOTHING
    """, (key, value, desc))
    print(f'  Inserted: {key}')

conn.commit()

# Verify
cur.execute("SELECT config_key, config_value, description FROM stock_config ORDER BY id")
print('\n=== Current config ===')
for row in cur.fetchall():
    print(f'  {row[0]}: {row[1]} ({row[2]})')

conn.close()
print('\nDone!')
