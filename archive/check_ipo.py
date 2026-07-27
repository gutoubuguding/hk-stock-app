import psycopg2

conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

print("=== IPO数据统计 ===")
cur.execute("SELECT COUNT(*) FROM stock_ipo")
print(f"IPO总数: {cur.fetchone()[0]}")

print("\n=== 即将上市新股 ===")
cur.execute("""
    SELECT stock_code, stock_name, listing_date, issue_price, entry_fee
    FROM stock_ipo
    WHERE listing_date >= CURRENT_DATE
    ORDER BY listing_date
    LIMIT 10
""")
for r in cur.fetchall():
    print(f"  {r[0]} {r[1]}: 上市日={r[2]} 发行价={r[3]} 入场费={r[4]}")

print("\n=== 近一年新股(按上市日期) ===")
cur.execute("""
    SELECT stock_code, stock_name, listing_date, issue_price,
           first_day_change, seven_day_change, thirty_day_change, current_change
    FROM stock_ipo
    WHERE listing_date >= CURRENT_DATE - INTERVAL '1 year'
    ORDER BY listing_date DESC
    LIMIT 10
""")
for r in cur.fetchall():
    print(f"  {r[0]} {r[1]}: 上市={r[2]} 发行={r[3]} 首日={r[4]} 7天={r[5]} 30天={r[6]} 现涨跌={r[7]}")

print("\n=== AI分析测试 ===")
import urllib.request
import json
try:
    req = urllib.request.urlopen('http://localhost:8080/api/ipo/list?days=30', timeout=10)
    data = json.loads(req.read())
    print(f"IPO列表API返回: {len(data)} 条")
    if data:
        print(f"  第一条: {data[0]}")
except Exception as e:
    print(f"API调用失败: {e}")

try:
    req2 = urllib.request.urlopen('http://localhost:8080/api/ipo/upcoming', timeout=10)
    data2 = json.loads(req2.read())
    print(f"\n即将上市API返回: {len(data2)} 条")
    if data2:
        print(f"  第一条: {data2[0]}")
except Exception as e:
    print(f"即将上市API失败: {e}")

cur.close(); conn.close()