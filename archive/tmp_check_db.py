import psycopg2
conn=psycopg2.connect(host='localhost',dbname='hk_stock',user='postgres',password='pc20050218')
cur=conn.cursor()
cur.execute('select count(*) from news')
print('news count', cur.fetchone()[0])
cur.execute("SELECT * FROM news WHERE stock_code = %s AND publish_time >= NOW() - (%s * INTERVAL '1 day') ORDER BY publish_time DESC", ('00700', 7))
print('query rows', len(cur.fetchall()))
