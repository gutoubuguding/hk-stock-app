#!/usr/bin/env python3
"""从 akshare 拉取全部港股数据并存入 PostgreSQL"""
import os
os.environ['NO_PROXY'] = '*'

import akshare as ak
import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432, database="hk_stock",
    user="postgres", password="pc20050218"
)
cur = conn.cursor()

print("Fetching ALL HK stocks...")

try:
    df = ak.stock_hk_spot()
    print(f"Got {len(df)} HK stocks")
    
    count = 0
    for _, row in df.iterrows():
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
            conn.rollback()
            continue
    
    conn.commit()
    
    cur.execute("SELECT COUNT(*) FROM stock_info")
    total = cur.fetchone()[0]
    print(f"Done! Total stocks in DB: {total}")
    
except Exception as e:
    print(f"Error: {e}")
    conn.rollback()
finally:
    cur.close()
    conn.close()
