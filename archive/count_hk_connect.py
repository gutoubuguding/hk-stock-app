import psycopg2

conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Get all stocks that have recent K-line data (successfully synced)
cur.execute("""
    SELECT COUNT(DISTINCT stock_code)
    FROM stock_kline
    WHERE period_type = 'D'
    AND trade_date >= '2026-04-01'
""")
recent_stocks = cur.fetchone()[0]
print(f"4月份有K线数据的股票: {recent_stocks} 只")

# Total stocks with any K-line data
cur.execute("SELECT COUNT(DISTINCT stock_code) FROM stock_kline WHERE period_type = 'D'")
total_with_data = cur.fetchone()[0]
print(f"总共有K线数据的股票: {total_with_data} 只")

# How many have today's data
cur.execute("""
    SELECT COUNT(DISTINCT stock_code)
    FROM stock_kline
    WHERE period_type = 'D' AND trade_date = '2026-04-20'
""")
today_count = cur.fetchone()[0]
print(f"今日(04-20)有数据的股票: {today_count} 只")

# Show top stocks by market cap with recent data
cur.execute("""
    SELECT k.stock_code, s.stock_name, k.trade_date, k.close_price
    FROM (
        SELECT stock_code, MAX(trade_date) as latest_date
        FROM stock_kline
        WHERE period_type = 'D'
        GROUP BY stock_code
    ) mk
    JOIN stock_kline k ON k.stock_code = mk.stock_code AND k.trade_date = mk.latest_date AND k.period_type = 'D'
    JOIN stock_info s ON k.stock_code = s.stock_code
    WHERE k.trade_date >= '2026-04-15'
    ORDER BY s.market_cap DESC NULLS LAST
    LIMIT 30
""")
print("\n主流股票最新数据 (按市值):")
print(f"{'代码':<8} {'名称':<15} {'最新日期':<12} {'收盘价'}")
print("-" * 50)
for r in cur.fetchall():
    print(f"{r[0]:<8} {r[1][:12]:<15} {str(r[2]):<12} {r[3]}")

cur.close(); conn.close()