import akshare as ak
import inspect

# Find HK IPO related functions
funcs = [name for name in dir(ak) if 'hk' in name.lower() and 'ipo' in name.lower()]
print("HK IPO funcs:", funcs)

# Also try stock_hk_* functions
hk_funcs = [name for name in dir(ak) if name.startswith('stock_hk')]
print("\nstock_hk functions:", hk_funcs[:20])