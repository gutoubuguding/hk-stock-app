import psycopg2
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

fields = ['subscription_end', 'pricing_date', 'allotment_date', 'cornerstone_investor', 
          'cornerstone_amount', 'fundraising_amount', 'public_offering_ratio', 
          'international_placement_ratio', 'issue_pe', 'industry_avg_pe',
          'seven_day_change', 'thirty_day_change', 'current_change']

for f in fields:
    cur.execute(f"SELECT COUNT(*) FROM stock_ipo WHERE listing_date >= '2025-01-01' AND {f} IS NOT NULL")
    print(f'{f}: {cur.fetchone()[0]}')