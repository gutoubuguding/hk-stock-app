import akshare as ak

print('=== Testing stock_ipo_hk_ths ===')
try:
    df = ak.stock_ipo_hk_ths()
    print(f'Shape: {df.shape}')
    print(f'Columns: {list(df.columns)}')
    print()
    print(df.head(10).to_string())
except Exception as e:
    print(f'Error: {e}')

print('\n\n=== Testing stock_ipo_info ===')
try:
    df2 = ak.stock_ipo_info()
    print(f'Shape: {df2.shape}')
    print(f'Columns: {list(df2.columns)}')
    print(df2.head(5).to_string())
except Exception as e:
    print(f'Error: {e}')
