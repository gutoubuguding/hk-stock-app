#!/usr/bin/env python3
"""调试同步脚本"""
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

# 获取前5只没有K线的股票
cur.execute("""
    SELECT s.stock_code, s.stock_name
    FROM stock_info s
    LEFT JOIN (SELECT DISTINCT stock_code FROM stock_kline WHERE period_type = 'D') k 
        ON s.stock_code = k.stock_code
    WHERE k.stock_code IS NULL
    ORDER BY s.stock_code
    LIMIT 5
""")
stocks = cur.fetchall()
print(f"测试 {len(stocks)} 只股票")

quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

for code, name in stocks:
    futu_code = f"HK.{code}"
    print(f"\n{code} {name}:")
    try:
        ret, data, err = quote_ctx.request_history_kline(futu_code, ktype=KLType.K_DAY, max_count=5)
        print(f"  返回码: {ret}")
        if ret != RET_OK:
            print(f"  错误: {err}")
        else:
            print(f"  成功: {len(data)} 条")
    except Exception as e:
        print(f"  异常: {e}")

quote_ctx.close()
cur.close()
conn.close()
