import akshare as ak
import psycopg2

# Try to get IPO data from AKShare
try:
    df = ak.stock_hk_ipo_summary()
    print("AKShare IPO columns:", df.columns.tolist())
    print("Shape:", df.shape)
    print(df.head(3))
except Exception as e:
    print(f"Error: {e}")