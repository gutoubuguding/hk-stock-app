#!/usr/bin/env python3
"""Sync recent K-line data for main stocks"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
from futu import OpenQuoteContext, RET_OK, KLType
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

# 主要股票列表
stocks = ['HK.00700', 'HK.09988', 'HK.03690', 'HK.01810', 'HK.09618', 
          'HK.02318', 'HK.00388', 'HK.01299', 'HK.02020', 'HK.01024']

print('Connecting to Futu OpenD...')
quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

total = 0
for code in stocks:
    stock_code = code.replace('HK.', '')
    print(f'Syncing {code}...')
    ret, data, _ = quote_ctx.request_history_kline(code, ktype=KLType.K_DAY, max_count=250)
    if ret != RET_OK:
        print(f'  Error: {data}')
        continue
    
    count = 0
    for _, row in data.iterrows():
        try:
            cur.execute('''
                INSERT INTO stock_kline (stock_code, period_type, trade_date, open_price, close_price, high_price, low_price, volume, turnover, change_percent, turnover_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (stock_code, period_type, trade_date) DO UPDATE SET
                    open_price = EXCLUDED.open_price,
                    close_price = EXCLUDED.close_price,
                    high_price = EXCLUDED.high_price,
                    low_price = EXCLUDED.low_price,
                    volume = EXCLUDED.volume,
                    turnover = EXCLUDED.turnover,
                    change_percent = EXCLUDED.change_percent,
                    turnover_rate = EXCLUDED.turnover_rate
            ''', (stock_code, 'D', row['time_key'], row['open'], row['close'], row['high'], row['low'], row['volume'], row['turnover'], row.get('change_rate', 0), row.get('turnover_rate', 0)))
            count += 1
        except Exception as e:
            print(f'  Error: {e}')
    
    conn.commit()
    total += count
    print(f'  Synced {count} records')

quote_ctx.close()
cur.close()
conn.close()
print(f'Total synced: {total} records')
