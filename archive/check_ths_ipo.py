import akshare as ak

# Try THS HK IPO data
try:
    df = ak.stock_ipo_hk_ths()
    print("Columns:", df.columns.tolist())
    print("Shape:", df.shape)
    print(df.head(3))
except Exception as e:
    print(f"Error: {e}")