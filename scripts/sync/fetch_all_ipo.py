#!/usr/bin/env python3
"""从东方财富获取完整港股新股数据"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False
import psycopg2
import sys
sys.stdout.reconfigure(encoding='utf-8')

conn = psycopg2.connect(
    host="localhost", port=5432, database="hk_stock",
    user="postgres", password="pc20050218"
)
cur = conn.cursor()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Referer": "https://quote.eastmoney.com/"
}

# 东方财富港股列表API - 获取所有港股
url = "https://push2.eastmoney.com/api/qt/clist/get"

all_stocks = []

# 分页获取
for page in range(1, 10):
    params = {
        "pn": page,
        "pz": 100,
        "po": 1,
        "np": 1,
        "ut": "bd1d9ddb04089700cf9c27f6f7426281",
        "fltt": 2,
        "invt": 2,
        "fid": "f26",  # 按上市日期排序
        "fs": "m:128+t:3,m:128+t:4,m:128+t:1,m:128+t:2",  # 港股
        "fields": "f2,f12,f14,f17,f18,f20,f21,f26,f115",  # 最新价,代码,名称,开盘,收盘,最高,最低,上市日期,总市值
    }
    
    try:
        resp = requests.get(url, params=params, headers=headers, timeout=15)
        data = resp.json()
        
        if data.get("data") and data["data"].get("diff"):
            items = data["data"]["diff"]
            if not items:
                break
            
            for item in items:
                listing_date_num = item.get("f26", 0)
                if listing_date_num and listing_date_num >= 20250101:
                    stock = {
                        "code": str(item.get("f12", "")).zfill(5),
                        "name": item.get("f14", ""),
                        "listing_date_num": listing_date_num,
                        "market_cap": item.get("f20", 0),  # 总市值
                    }
                    all_stocks.append(stock)
            
            print(f"Page {page}: got {len(items)} items, {len(all_stocks)} IPOs since 2025")
        else:
            break
    except Exception as e:
        print(f"Error page {page}: {e}")
        break

print(f"\nTotal HK IPOs since 2025-01-01: {len(all_stocks)}")

# 显示部分数据
for s in all_stocks[:10]:
    date_str = str(s["listing_date_num"])
    date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
    print(f"  {s['code']} - {s['name']} | {date_fmt} | 市值: {s['market_cap']}")

# 写入数据库
count = 0
for s in all_stocks:
    try:
        date_str = str(s["listing_date_num"])
        date_fmt = f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:]}"
        
        cur.execute("""
            INSERT INTO stock_ipo (stock_code, stock_name, listing_date, updated_at)
            VALUES (%s, %s, %s, NOW())
            ON CONFLICT (stock_code) DO UPDATE SET
                stock_name = EXCLUDED.stock_name,
                listing_date = EXCLUDED.listing_date,
                updated_at = NOW()
        """, (s["code"], s["name"], date_fmt))
        count += 1
    except Exception as e:
        conn.rollback()
        continue

conn.commit()
print(f"\nInserted/Updated {count} IPO records")

# 验证
cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01'")
total = cur.fetchone()[0]
print(f"Total IPOs in DB since 2025-01-01: {total}")

cur.close()
conn.close()
print("Done!")
