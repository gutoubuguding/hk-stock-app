#!/usr/bin/env python3
"""Test Futu OpenD IPO list via Futu API"""
import sys
sys.path.insert(0, r'C:\Users\34596\AppData\Local\Programs\Python\Python313\Lib\site-packages')

from futu import *

# Futu OpenD connection settings
HOST = '127.0.0.1'
PORT = 11111

print(f"Connecting to Futu OpenD at {HOST}:{PORT}...")

# Create quote context with timeout
quote_ctx = OpenQuoteContext(host=HOST, port=PORT, is_encrypt=False)
quote_ctx.set_sync_query_connect_timeout(5)
print(f"Context created. Status: {quote_ctx.status}")

# Try to get HK IPO list
print("\nRequesting HK IPO list...")
try:
    ret, data = quote_ctx.get_ipo_list(market=Market.HK)
    print(f"Return code: {ret}")
    print(f"Data type: {type(data)}")
    if data is not None:
        print(f"Shape: {data.shape if hasattr(data, 'shape') else 'N/A'}")
        print(f"Columns: {list(data.columns) if hasattr(data, 'columns') else data}")
        print(data.head(10).to_string() if hasattr(data, 'head') else str(data)[:500])
    else:
        print(f"No data returned")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

# Close context
quote_ctx.close()
print("\nDone.")
