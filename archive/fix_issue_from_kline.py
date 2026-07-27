import akshare as ak
import psycopg2

conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Get missing issue_price stocks
cur.execute("SELECT stock_code, stock_name, listing_date FROM stock_ipo WHERE listing_date >= '2025-01-01' AND issue_price IS NULL ORDER BY listing_date")
stocks = cur.fetchall()
print(f"Missing issue_price: {len(stocks)} stocks")

for code, name, listing_date in stocks:
    if listing_date is None:
        print(f"{code} {name}: no listing date, skipping")
        continue
    
    listing_str = listing_date.strftime('%Y-%m-%d') if hasattr(listing_date, 'strftime') else str(listing_date)
    print(f"\n{code} {name} (listing: {listing_str})")
    
    try:
        # Try to get daily data to find listing day open price
        df = ak.stock_hk_daily(symbol=code, adjust='')
        if df is not None and not df.empty:
            df['date'] = df['date'].astype(str)
            first_day = df[df['date'] == listing_str]
            if not first_day.empty:
                open_p = float(first_day.iloc[0]['open'])
                close_p = float(first_day.iloc[0]['close'])
                print(f"  Open: {open_p}, Close: {close_p}")
                
                # The issue_price should be close to open price on listing day
                # Update in DB
                cur.execute("""
                    UPDATE stock_ipo 
                    SET issue_price = %s, updated_at = NOW()
                    WHERE stock_code = %s
                """, (open_p, code))
                print(f"  -> Set issue_price = {open_p}")
            else:
                print(f"  No data for listing date {listing_str}, first available: {df['date'].min()}")
        else:
            print(f"  No K-line data returned")
    except Exception as e:
        print(f"  Error: {e}")

conn.commit()
print("\nDone")