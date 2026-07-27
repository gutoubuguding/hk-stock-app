#!/usr/bin/env python3
"""同步2025年港股IPO数据"""
import sys
import os
os.environ['NO_PROXY'] = '*'

sys.stdout.reconfigure(encoding='utf-8')
from futu import OpenQuoteContext, Market, RET_OK
import psycopg2
from datetime import datetime

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

FUTU_HOST = os.getenv('FUTU_OPEND_HOST', 'host.docker.internal')
FUTU_PORT = int(os.getenv('FUTU_OPEND_PORT', '11111'))

print("同步2025年港股IPO数据...")

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

# 从Futu获取IPO列表
quote_ctx = OpenQuoteContext(host=FUTU_HOST, port=FUTU_PORT, is_encrypt=False)

# 获取港股IPO列表
ret, data = quote_ctx.get_ipo_list(market=Market.HK)
if ret != RET_OK:
    print(f"获取IPO列表失败: {data}")
    quote_ctx.close()
    cur.close()
    conn.close()
    sys.exit(1)

print(f"获取到 {len(data)} 条IPO记录")

# 过滤2025年的数据
ipo_2025 = []
for _, row in data.iterrows():
    code = row.get('code', '')
    if not code or code == 'N/A':
        continue
    
    stock_code = code.replace('HK.', '')
    stock_name = str(row.get('name', '')).strip()
    if stock_name == 'N/A':
        stock_name = ''
    
    listing_date = row.get('list_time', '')
    list_date = None
    if listing_date and listing_date != 'N/A':
        try:
            list_date = datetime.strptime(listing_date[:10], '%Y-%m-%d').date()
        except:
            pass
    
    # 只处理2025年的数据
    if list_date and list_date.year == 2025:
        ipo_2025.append({
            'stock_code': stock_code,
            'stock_name': stock_name,
            'listing_date': list_date,
            'status': 'listed'
        })

quote_ctx.close()

print(f"找到 {len(ipo_2025)} 条2025年IPO记录")

# 插入数据库
inserted = 0
for ipo in ipo_2025:
    try:
        cur.execute("""
            INSERT INTO stock_ipo (stock_code, stock_name, listing_date, status)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (stock_code) DO UPDATE SET
                stock_name = EXCLUDED.stock_name,
                listing_date = EXCLUDED.listing_date,
                status = EXCLUDED.status
        """, (ipo['stock_code'], ipo['stock_name'], ipo['listing_date'], ipo['status']))
        inserted += cur.rowcount
    except Exception as e:
        print(f"插入失败 {ipo['stock_code']}: {e}")

conn.commit()
cur.close()
conn.close()

print(f"\n成功插入/更新 {inserted} 条2025年IPO记录")
