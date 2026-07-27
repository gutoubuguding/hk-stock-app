#!/usr/bin/env python3
"""从 akshare 拉取港股数据并存入 PostgreSQL"""
import os
os.environ['NO_PROXY'] = '*'

import akshare as ak
import psycopg2

# 数据库连接
conn = psycopg2.connect(
    host="localhost",
    port=5432,
    database="hk_stock",
    user="postgres",
    password="pc20050218"
)
cur = conn.cursor()

print("Start fetching HK stock list...")

try:
    # 获取港股实时行情
    df = ak.stock_hk_spot()
    print(f"Got {len(df)} HK stocks")
    
    # 插入股票信息
    count = 0
    for _, row in df.head(100).iterrows():  # 先插入100条
        try:
            stock_code = str(row['代码']).zfill(5)
            stock_name = str(row['中文名称'])
            
            cur.execute("""
                INSERT INTO stock_info (stock_code, stock_name, updated_at)
                VALUES (%s, %s, NOW())
                ON CONFLICT (stock_code) DO UPDATE SET
                    stock_name = EXCLUDED.stock_name,
                    updated_at = NOW()
            """, (stock_code, stock_name))
            count += 1
        except Exception as e:
            print(f"Insert failed {stock_code}: {e}")
            conn.rollback()
            continue
    
    conn.commit()
    print(f"Successfully inserted {count} stocks")
    
    # 验证数据
    cur.execute("SELECT COUNT(*) FROM stock_info")
    total = cur.fetchone()[0]
    print(f"Total stocks in DB: {total}")
    
    # 查询腾讯
    cur.execute("SELECT stock_code, stock_name FROM stock_info WHERE stock_code = '00700'")
    result = cur.fetchone()
    if result:
        print(f"Found Tencent: {result[0]} - {result[1]}")
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
    conn.rollback()
finally:
    cur.close()
    conn.close()

print("Done!")
