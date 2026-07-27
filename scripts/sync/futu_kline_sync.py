#!/usr/bin/env python3
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

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

cur.execute("""
    SELECT stock_code FROM stock_info 
    WHERE stock_code NOT IN (
        SELECT stock_code FROM stock_kline 
        WHERE period_type = 'D' AND trade_date = '2026-07-24'
    )
    ORDER BY stock_code
    LIMIT 500
""")
stocks = [row[0] for row in cur.fetchall()]
print(f"需要同步: {len(stocks)} 只股票")

quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

updated = 0
for i, code in enumerate(stocks):
    try:
        ret, data, _ = quote_ctx.request_history_kline(
            f'HK.{code}', ktype=KLType.K_DAY, autype=None,
            start='2026-07-24', end='2026-07-25'
        )
        if ret == RET_OK and len(data) > 0:
            for _, row in data.iterrows():
                cur.execute("""
                    INSERT INTO stock_kline (stock_code, period_type, trade_date, open_price, close_price, high_price, low_price, volume, turnover, change_percent)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (stock_code, period_type, trade_date) DO UPDATE SET
                        close_price = EXCLUDED.close_price, volume = EXCLUDED.volume, change_percent = EXCLUDED.change_percent
                """, (code, 'D', str(row['time_key'])[:10], float(row['open']), float(row['close']), float(row['high']), float(row['low']), int(row['volume']), float(row['turnover']), float(row.get('change_rate', 0))))
            updated += 1
            if updated % 50 == 0:
                print(f"  {updated}...")
                conn.commit()
    except Exception as e:
        pass

conn.commit()
quote_ctx.close()
cur.close()
conn.close()
print(f"完成: {updated} 只")
