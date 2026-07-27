import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01'")
total = cur.fetchone()[0]

fields = [
    'sector', 'subscription_start', 'subscription_end', 'pricing_date', 
    'allotment_date', 'listing_date', 'lot_size', 'issue_price', 'entry_fee',
    'fundraising_amount', 'allotment_rate', 'oversubscription_ratio',
    'public_offering_ratio', 'international_placement_ratio',
    'sponsor', 'cornerstone_investor', 'cornerstone_amount',
    'issue_pe', 'industry_avg_pe', 'is_hk_stock_connect',
    'first_day_change', 'seven_day_change', 'thirty_day_change', 'current_change'
]

print(f"总股票数: {total}")
print(f"{'字段':<30} {'已填充':<10} {'缺失':<10} {'完成率':<10}")
print("-" * 60)
for f in fields:
    cur.execute(f"SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01' AND {f} IS NOT NULL")
    cnt = cur.fetchone()[0]
    miss = total - cnt
    pct = round(cnt/total*100, 1)
    status = "OK" if cnt == total else "HIGH" if cnt > total*0.8 else "MED" if cnt > total*0.5 else "LOW"
    print(f"{f:<30} {cnt:<10} {miss:<10} {pct}% {status}")