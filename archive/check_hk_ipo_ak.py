import akshare as ak
import pandas as pd

# Try to get HK IPO data from akshare - check what functions are available
print('=== Trying stock_hk_main_board_spot_em for reference ===')
try:
    df = ak.stock_hk_main_board_spot_em()
    print(f'Shape: {df.shape}')
    print(f'Columns: {list(df.columns)}')
    # Filter for recently listed stocks
    if '上市日期' in df.columns:
        recent = df[df['上市日期'] > '2026-01-01'].head(20)
        print(recent[['代码', '名称', '上市日期']].to_string())
except Exception as e:
    print(f'Error: {e}')

# Try the HK IPO specific function from THS
print('\n=== stock_ipo_hk_ths detailed check ===')
try:
    df2 = ak.stock_ipo_hk_ths()
    print(f'Columns: {list(df2.columns)}')
    # Print all column names with proper encoding
    for col in df2.columns:
        print(f'  "{col}"')
    # Print first row fully
    if len(df2) > 0:
        print('\nFirst row:')
        for col in df2.columns:
            print(f'  {col}: {df2.iloc[0][col]}')
except Exception as e:
    print(f'Error: {e}')
