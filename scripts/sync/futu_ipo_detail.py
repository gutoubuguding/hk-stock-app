import sys
sys.stdout.reconfigure(encoding='utf-8')

from futu import *
import json

print('Connecting to Futu OpenD...')
quote_ctx = OpenQuoteContext(host='127.0.0.1', port=11111)
print('Connected!')

# Try to get IPO data with allocation info
print('\n=== Getting HK IPO list ===')
ret, data = quote_ctx.get_ipo_list(Market.HK)
if ret == RET_OK:
    print(f'Got {len(data)} records')
    print(f'Columns: {data.columns.tolist()}')
    for i, row in data.iterrows():
        code = row.get('code', '')
        name = row.get('name', '')
        winning_ratio = row.get('winning_ratio', '')
        is_has_won = row.get('is_has_won', '')
        winning_num_data = row.get('winning_num_data', '')
        print(f'  {code} {name}: winning_ratio={winning_ratio}, is_has_won={is_has_won}')
else:
    print(f'Error: {data}')

# Try to get more IPO info
print('\n=== Trying to get IPO details ===')
# Check if there's a way to get historical IPO data
try:
    # Try to get specific stock IPO info
    stock_codes = ['HK.06636', 'HK.01021', 'HK.02726', 'HK.02526']
    for code in stock_codes:
        ret, data = quote_ctx.get_stock_basicinfo(Market.HK, SecurityType.STOCK, code)
        if ret == RET_OK:
            for i, row in data.iterrows():
                print(f'  {code}: {row.to_dict()}')
        else:
            print(f'  {code}: {data}')
except Exception as e:
    print(f'Error: {e}')

quote_ctx.close()
print('\nDone')
