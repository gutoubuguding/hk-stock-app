import psycopg2
import requests
from bs4 import BeautifulSoup
import re
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# The 4 IPOs from AASTOCKS sidebar with correct data
# We now know the correct names from Futu:
# HK.06636 极视角 - lot_size=50
# HK.01021 华沿机器人 - lot_size=200
# HK.02726 瀚天天成 - lot_size=50
# HK.02526 德适-B - lot_size=50

# AASTOCKS data (ordered by oversubscription ratio):
# Row 0: oversubscription=5058.4, rate=5.0%, entry=?  -> 华沿机器人 (highest oversubscription)
# Row 1: oversubscription=1072.4, rate=3.0%, entry=?  -> 德适-B
# Row 2: oversubscription=49.7, rate=20.0%, entry=?   -> 瀚天天成 (lowest oversubscription)
# Row 3: oversubscription=4590.4, rate=10.0%, entry=? -> 极视角

# Let's verify by checking each stock's page on AASTOCKS for entry fee
stocks_to_check = [
    ('06636', '极视角', 4590.4, 10.0),
    ('01021', '华沿机器人', 5058.4, 5.0),
    ('02726', '瀚天天成', 49.7, 20.0),
    ('02526', '德适-B', 1072.4, 3.0),
]

# Verify entry fees from AASTOCKS individual pages
print('=== Verifying entry fees from AASTOCKS ===')
for code, name, ratio, rate in stocks_to_check:
    url = f'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol={code}'
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Look for entry fee in the IPO detail table
        tables = soup.find_all('table')
        entry_fee = None
        issue_price = None
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                for i, cell in enumerate(cells):
                    if '入场' in cell and i+1 < len(cells):
                        val = cells[i+1].replace(',', '').replace('港', '').strip()
                        try:
                            entry_fee = float(val)
                        except:
                            pass
                    if '招股价' in cell and i+1 < len(cells):
                        val = cells[i+1].replace(',', '').strip()
                        try:
                            issue_price = float(val)
                        except:
                            pass
                    if '公开发售' in cell and '股' in cell:
                        # Look for public offering shares
                        pass
        
        print(f'{code} {name}: entry_fee={entry_fee}, issue_price={issue_price}, ratio={ratio}, rate={rate}%')
        
        # Update database
        conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
        cur = conn.cursor()
        
        updates = ['allotment_rate = %s', 'oversubscription_ratio = %s']
        params = [rate, ratio]
        
        if entry_fee:
            updates.append('entry_fee = %s')
            params.append(entry_fee)
        
        if issue_price:
            updates.append('issue_price = %s')
            params.append(issue_price)
        
        params.append(f'HK.{code}')
        sql = f"UPDATE stock_ipo SET {', '.join(updates)} WHERE stock_code = %s"
        cur.execute(sql, params)
        conn.commit()
        print(f'  -> DB updated ({cur.rowcount} rows)')
        conn.close()
        
    except Exception as e:
        print(f'{code} Error: {e}')
    
    time.sleep(1)

# Now let's verify the data
print('\n=== Verification ===')
conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()
cur.execute("""
    SELECT stock_code, stock_name, listing_date, allotment_rate, oversubscription_ratio, entry_fee, issue_price
    FROM stock_ipo 
    WHERE allotment_rate IS NOT NULL
    ORDER BY listing_date DESC
""")
for row in cur.fetchall():
    print(f'  {row[0]} {row[1]} ({row[2]}): rate={row[3]}%, ratio={row[4]}, entry={row[5]}, price={row[6]}')
conn.close()
