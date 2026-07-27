import requests, psycopg2, json, sys
BASE='http://localhost:8080'
endpoints=[
('dashboard','/api/calendar/market-overview'),
('search','/api/stock/search?keyword=00700'),
('kline_D','/api/stock/kline?stockCode=00700&periodType=D&days=5'),
('kline_5D','/api/stock/kline?stockCode=00700&periodType=5D&days=5'),
('kline_M','/api/stock/kline?stockCode=00700&periodType=M&days=5'),
('kline_Y','/api/stock/kline?stockCode=00700&periodType=Y&days=5'),
('daily','/api/stock/daily-info?stockCode=00700'),
('valuation','/api/stock/valuation?stockCode=00700'),
('watchlist','/api/watchlist'),
('ipo_upcoming','/api/ipo/upcoming'),
('ipo_comparison','/api/ipo/comparison'),
('ipo_sector','/api/ipo/sector-stats'),
('ipo_break','/api/ipo/break-rate'),
('calendar_fin','/api/calendar/financial?days=60'),
('calendar_div','/api/calendar/dividend?days=60'),
('alerts','/api/alert'),
('compare','/api/compare?stockCodes=00700,09988'),
('news_list','/api/news/list?stockCode=00700&days=7'),
]
for name,path in endpoints:
    try:
        r=requests.get(BASE+path,timeout=8)
        data=r.json() if r.text else None
        if isinstance(data,list): summary=f'list len={len(data)} sample={data[:1]}'
        elif isinstance(data,dict): summary=f'dict keys={list(data.keys())[:8]} sample={str(data)[:220]}'
        else: summary=str(data)[:120]
        print(f'{name}: HTTP {r.status_code} {summary}')
    except Exception as e:
        print(f'{name}: ERR {e}')

conn=psycopg2.connect(host='localhost',port=5432,dbname='hk_stock',user='postgres',password='pc20050218')
cur=conn.cursor()
for table in ['stock_info','stock_kline','stock_ipo','stock_valuation','stock_calendar','news','price_alert','watchlist']:
    cur.execute(f'select count(*) from {table}')
    print(f'table {table}: {cur.fetchone()[0]}')
cur.execute("select period_type,count(*) from stock_kline group by period_type order by period_type")
print('kline periods:',cur.fetchall())
cur.close(); conn.close()
