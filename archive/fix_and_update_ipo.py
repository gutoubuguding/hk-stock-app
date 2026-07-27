import psycopg2
import requests
from bs4 import BeautifulSoup
import re
import time

# First, reset incorrect allotment_rate values (all were set to 5.0 incorrectly)
conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute("UPDATE stock_ipo SET allotment_rate = NULL WHERE allotment_rate = 5.0")
print(f'Reset {cur.rowcount} incorrect allotment_rate values')
conn.commit()
conn.close()

# Now let's get the correct data from AASTOCKS
# The sidebar table (Table 30) shows recent 4 IPOs
# Let's match them with our database by listing date

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

def get_ipo_summary():
    """Get IPO allocation summary from AASTOCKS"""
    url = 'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol=01021'
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    tables = soup.find_all('table')
    
    # Find the allocation summary table (has headers: 公司名称, 认购倍数, 一手中签率, 申购一手)
    for table in tables:
        rows = table.find_all('tr')
        if len(rows) >= 5:
            first_row_text = ''.join([td.get_text(strip=True) for td in rows[0].find_all(['td', 'th'])])
            if '倍' in first_row_text and '签' in first_row_text:
                print(f'Found allocation table with {len(rows)} rows')
                result = []
                for row in rows[1:]:
                    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                    if len(cells) >= 4:
                        # cells[0] = company name (encoded)
                        # cells[1] = oversubscription ratio
                        # cells[2] = one-lot success rate (%)
                        # cells[3] = entry fee (HKD)
                        rate_str = cells[2].replace('%', '').strip()
                        ratio_str = cells[1].replace(',', '').strip()
                        fee_str = cells[3].replace('港', '').replace(',', '').strip()
                        
                        try:
                            rate = float(rate_str)
                        except:
                            rate = None
                        try:
                            ratio = float(ratio_str)
                        except:
                            ratio = None
                        try:
                            fee = float(fee_str)
                        except:
                            fee = None
                        
                        result.append({
                            'name': cells[0],
                            'oversubscription_ratio': ratio,
                            'allotment_rate': rate,
                            'entry_fee': fee,
                        })
                return result
    return []

# Get allocation data
allocations = get_ipo_summary()
print(f'\nFound {len(allocations)} IPO allocations from AASTOCKS:')
for a in allocations:
    print(f'  {a["name"]}: 一手中签率={a["allotment_rate"]}%, 认购倍数={a["oversubscription_ratio"]}, 入场费={a["entry_fee"]}')

# Now get our database IPOs for the matching dates
conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# Get all listed IPOs with their names
cur.execute("""
    SELECT stock_code, stock_name, listing_date 
    FROM stock_ipo 
    WHERE listing_date IS NOT NULL 
    AND listing_date <= CURRENT_DATE
    AND allotment_rate IS NULL
    ORDER BY listing_date DESC
""")
db_ipos = cur.fetchall()

print(f'\nDatabase has {len(db_ipos)} IPOs without allotment_rate:')
for code, name, date in db_ipos[:10]:
    print(f'  {code} {name} ({date})')

# The AASTOCKS sidebar shows the most recent 4 IPOs that have allocation results
# These are typically the IPOs that listed most recently
# Let's try to match by looking at the listing dates

# Get distinct listing dates
cur.execute("""
    SELECT DISTINCT listing_date 
    FROM stock_ipo 
    WHERE listing_date IS NOT NULL 
    AND listing_date <= CURRENT_DATE
    ORDER BY listing_date DESC
    LIMIT 10
""")
dates = [row[0] for row in cur.fetchall()]
print(f'\nRecent listing dates: {dates}')

conn.close()
