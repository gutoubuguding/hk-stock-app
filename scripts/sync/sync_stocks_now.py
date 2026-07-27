#!/usr/bin/env python3
"""Sync stocks from Futu OpenD to database"""
import sys
sys.stdout.reconfigure(encoding='utf-8')

from futu import OpenQuoteContext, RET_OK, Market
import psycopg2
import os

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

FUTU_HOST = os.getenv('FUTU_OPEND_HOST', 'host.docker.internal')
FUTU_PORT = int(os.getenv('FUTU_OPEND_PORT', '11111'))

print('Connecting to Futu OpenD...')
quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)
quote_ctx.set_sync_query_connect_timeout(10)

print('Getting stock list...')
ret, data = quote_ctx.get_stock_basicinfo(Market.HK)
quote_ctx.close()

if ret != RET_OK:
    print(f'Error: {data}')
    sys.exit(1)

print(f'Got {len(data)} stocks')

# Filter stocks (stock_type == "STOCK" means regular stocks)
stocks = data[data['stock_type'] == 'STOCK']
print(f'Filtered to {len(stocks)} regular stocks')

# Save to database
conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

count = 0
for _, row in stocks.iterrows():
    try:
        cur.execute("""
            INSERT INTO stock_info (stock_code, stock_name, is_hk_stock_connect)
            VALUES (%s, %s, %s)
            ON CONFLICT (stock_code) DO UPDATE SET
                stock_name = EXCLUDED.stock_name
        """, (row['code'], row['name'], False))
        count += 1
    except Exception as e:
        print(f'Error inserting {row["code"]}: {e}')

conn.commit()
cur.close()
conn.close()

print(f'Synced {count} stocks to database')
