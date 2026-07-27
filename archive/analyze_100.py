import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Check how many stocks have each first_day_change value
cur.execute("""
    SELECT first_day_change, COUNT(*) as cnt
    FROM stock_ipo WHERE listing_date >= '2025-01-01' AND first_day_change IS NOT NULL
    GROUP BY first_day_change ORDER BY cnt DESC
""")
rows = cur.fetchall()
print(f"Unique first_day_change values: {len(rows)}")
print("\nDistribution:")
for change, cnt in rows:
    print(f"  {change}%: {cnt} stocks")

print()
# Check 03625 specifically - what did AKShare return for it?
import akshare as ak
try:
    df = ak.stock_hk_daily(symbol='03625', adjust='')
    df['date'] = df['date'].astype(str)
    listing_data = df[df['date'] == '2026-03-31']
    if not listing_data.empty:
        close = listing_data.iloc[0]['close']
        print(f"03625 傅里叶 first day close (2026-03-31): {close}")
    else:
        print("03625: No data for listing date")
        # Check nearby dates
        recent = df[df['date'] >= '2026-03-31'].head(5)
        print(recent[['date', 'open', 'close', 'high', 'low']])
except Exception as e:
    print(f"03625 error: {e}")