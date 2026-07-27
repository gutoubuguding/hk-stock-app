import requests
from bs4 import BeautifulSoup
import psycopg2
import re
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
}

# Column mapping (0-indexed):
# Cell 0: empty
# Cell 1: 公司名称+代码 (e.g., 华沿机器人01021.HK)
# Cell 2: 上市日期
# Cell 3: 每手股数
# Cell 4: 价格范围
# Cell 5: 发行价
# Cell 6: 招股价
# Cell 7: 认购倍数
# Cell 8: 入场费
# Cell 9: 一手中签率
# Cell 10: 首日收盘价
# Cell 11: 首日涨幅
# Cell 12: 累计涨幅

def scrape_ipo_page(page_num):
    url = f'http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx?s=3&o=0&page={page_num}'
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    tables = soup.find_all('table')
    
    # Find the IPO data table
    ipo_table = None
    for idx, table in enumerate(tables):
        rows = table.find_all('tr')
        if len(rows) > 5:
            first_row_text = ''.join([td.get_text(strip=True) for td in rows[0].find_all(['td', 'th'])])
            if 'HK' in first_row_text or '倍' in first_row_text:
                ipo_table = table
                break
    
    if not ipo_table:
        return []
    
    rows = ipo_table.find_all('tr')
    results = []
    
    for row in rows[1:]:  # Skip header
        cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
        if len(cells) < 10:
            continue
        
        # Cell 1: contains stock code
        code_match = re.search(r'(\d{5})\.HK', cells[1])
        if not code_match:
            continue
        
        stock_code = code_match.group(1)
        
        # Cell 9: 一手中签率
        rate_str = cells[9].replace('%', '').strip()
        try:
            allotment_rate = float(rate_str)
        except:
            allotment_rate = None
        
        # Cell 7: 认购倍数
        ratio_str = cells[7].replace(',', '').strip()
        try:
            oversubscription_ratio = float(ratio_str)
        except:
            oversubscription_ratio = None
        
        # Cell 8: 入场费
        fee_str = cells[8].replace(',', '').replace('港', '').strip()
        try:
            entry_fee = float(fee_str)
        except:
            entry_fee = None
        
        # Cell 5: 发行价
        price_str = cells[5].replace(',', '').strip()
        try:
            issue_price = float(price_str)
        except:
            issue_price = None
        
        results.append({
            'stock_code': stock_code,
            'allotment_rate': allotment_rate,
            'oversubscription_ratio': oversubscription_ratio,
            'entry_fee': entry_fee,
            'issue_price': issue_price,
        })
    
    return results

def update_database(records):
    conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
    cur = conn.cursor()
    
    updated = 0
    for r in records:
        if r['allotment_rate'] is None:
            continue
        
        cur.execute("""
            UPDATE stock_ipo 
            SET allotment_rate = %s,
                oversubscription_ratio = COALESCE(%s, oversubscription_ratio),
                entry_fee = COALESCE(%s, entry_fee),
                issue_price = COALESCE(%s, issue_price)
            WHERE stock_code = %s
            AND allotment_rate IS NULL
        """, (
            r['allotment_rate'],
            r['oversubscription_ratio'],
            r['entry_fee'],
            r['issue_price'],
            r['stock_code'],
        ))
        if cur.rowcount > 0:
            updated += cur.rowcount
    
    conn.commit()
    conn.close()
    return updated

if __name__ == '__main__':
    print('Starting HK IPO allocation data scrape...')
    total_records = 0
    total_updated = 0
    
    for page in range(1, 20):
        print(f'\nPage {page}...')
        try:
            records = scrape_ipo_page(page)
            if not records:
                print(f'  No records found, stopping.')
                break
            
            print(f'  Found {len(records)} records')
            for r in records:
                print(f'    {r["stock_code"]}: rate={r["allotment_rate"]}%, ratio={r["oversubscription_ratio"]}, entry={r["entry_fee"]}, price={r["issue_price"]}')
            
            updated = update_database(records)
            print(f'  DB updated: {updated} rows')
            total_records += len(records)
            total_updated += updated
            
            time.sleep(1)
            
        except Exception as e:
            print(f'  Error: {e}')
            import traceback
            traceback.print_exc()
            break
    
    print(f'\n=== Summary ===')
    print(f'Total records scraped: {total_records}')
    print(f'Total DB updates: {total_updated}')
    
    conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE allotment_rate IS NOT NULL")
    print(f'Database records with allotment_rate: {cur.fetchone()[0]}')
    cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE listing_date <= CURRENT_DATE")
    print(f'Total listed IPOs: {cur.fetchone()[0]}')
    conn.close()
