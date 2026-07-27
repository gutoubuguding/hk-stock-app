import psycopg2
conn=psycopg2.connect(host='localhost',port=5432,dbname='hk_stock',user='postgres',password='pc20050218')
cur=conn.cursor()
cur.execute("""
select count(*) total,
 count(*) filter (where listing_date <= current_date - interval '7 days' and seven_day_change is null and issue_price is not null) missing7,
 count(*) filter (where listing_date <= current_date - interval '30 days' and thirty_day_change is null and issue_price is not null) missing30,
 count(*) filter (where first_day_change is null and issue_price is not null and listing_date <= current_date) missing1
from stock_ipo where listing_date >= '2025-01-01'
""")
print('ipo gaps', cur.fetchone())
cur.execute("""
select stock_code, stock_name, listing_date, issue_price, first_day_change, seven_day_change, thirty_day_change,
 (select count(*) from stock_kline k where k.stock_code=i.stock_code and k.period_type='D' and k.trade_date>=i.listing_date) kcnt
from stock_ipo i
where listing_date >= '2025-01-01' and issue_price is not null
and ((listing_date <= current_date - interval '7 days' and seven_day_change is null) or (listing_date <= current_date - interval '30 days' and thirty_day_change is null) or first_day_change is null)
order by listing_date desc limit 30
""")
for r in cur.fetchall(): print(r)
cur.execute("select index_code,index_name,last_price,change_val,change_pct,raise_count,fall_count,equal_count,update_time from market_overview order by update_time desc limit 10")
print('market rows')
for r in cur.fetchall(): print(r)
cur.close(); conn.close()
