import akshare as ak
import psycopg2

# Verify 03625 first_day_change
conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

try:
    df = ak.stock_hk_daily(symbol='03625', adjust='')
    df['date'] = df['date'].astype(str)
    listing_data = df[df['date'] == '2026-03-31']
    if not listing_data.empty:
        close = float(listing_data.iloc[0]['close'])
        issue_price = 40.0
        calc_change = round((close - issue_price) / issue_price * 100, 2)
        print(f"03625 傅里叶: 收盘价={close}, 发行价=40, 计算涨幅={calc_change}%")
    else:
        print("03625: 无上市日数据")
        recent = df[df['date'] >= '2026-03-31'].head(3)
        print(recent[['date', 'close']])
except Exception as e:
    print(f"Error: {e}")