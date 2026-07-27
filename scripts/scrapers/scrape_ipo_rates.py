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

def scrape_ipo_detail(stock_code):
    """Scrape IPO detail from AASTOCKS for a specific stock code"""
    # Convert to AASTOCKS format (5-digit without HK. prefix)
    code = stock_code.replace('HK.', '').replace('.', '').zfill(5)
    url = f'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol={code}'
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        result = {
            'stock_code': stock_code,
            'allotment_rate': None,
            'oversubscription_ratio': None,
            'entry_fee': None,
            'issue_price': None,
            'sponsor': None,
        }
        
        # Get all text and look for patterns
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                
                for i, cell in enumerate(cells):
                    # 认购倍数
                    if '倍' in cell and i+1 < len(cells):
                        val = cells[i+1].replace(',', '').replace('倍', '').strip()
                        try:
                            result['oversubscription_ratio'] = float(val)
                        except:
                            pass
                    
                    # 中签率
                    if '中签' in cell:
                        for c in cells[i:]:
                            if '%' in c:
                                num = c.replace('%', '').replace('+', '').strip()
                                try:
                                    result['allotment_rate'] = float(num)
                                    break
                                except:
                                    pass
                    
                    # 入场费
                    if '入场' in cell and i+1 < len(cells):
                        val = cells[i+1].replace(',', '').replace('港', '').strip()
                        try:
                            result['entry_fee'] = float(val)
                        except:
                            pass
                    
                    # 招股价
                    if '招股价' in cell and i+1 < len(cells):
                        val = cells[i+1].replace(',', '').strip()
                        try:
                            result['issue_price'] = float(val)
                        except:
                            pass
                    
                    # 保荐人
                    if '保荐' in cell and i+1 < len(cells):
                        result['sponsor'] = cells[i+1][:200]  # Limit length
        
        # Also look for percentage values that might be allotment rates
        # Check table that has subscription/oversubscription data
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                cell_text = ' '.join(cells)
                
                # Look for pattern like "一手" + percentage
                if '一手' in cell_text or '中签' in cell_text:
                    for c in cells:
                        match = re.search(r'(\d+\.?\d*)%', c)
                        if match and not result['allotment_rate']:
                            result['allotment_rate'] = float(match.group(1))
        
        return result
    except Exception as e:
        print(f'  Error scraping {code}: {e}')
        return {'stock_code': stock_code, 'allotment_rate': None, 'oversubscription_ratio': None, 'entry_fee': None, 'issue_price': None, 'sponsor': None}

def update_db(data):
    """Update IPO record in database"""
    if not data.get('allotment_rate') and not data.get('oversubscription_ratio'):
        return False
    
    conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
    cur = conn.cursor()
    
    updates = []
    params = []
    
    if data.get('allotment_rate') is not None:
        updates.append('allotment_rate = %s')
        params.append(data['allotment_rate'])
    
    if data.get('oversubscription_ratio') is not None:
        updates.append('oversubscription_ratio = %s')
        params.append(data['oversubscription_ratio'])
    
    if data.get('entry_fee') is not None:
        updates.append('entry_fee = %s')
        params.append(data['entry_fee'])
    
    if data.get('issue_price') is not None:
        updates.append('issue_price = %s')
        params.append(data['issue_price'])
    
    if data.get('sponsor') is not None:
        updates.append('sponsor = %s')
        params.append(data['sponsor'])
    
    if not updates:
        conn.close()
        return False
    
    params.append(data['stock_code'])
    sql = f"UPDATE stock_ipo SET {', '.join(updates)} WHERE stock_code = %s"
    cur.execute(sql, params)
    conn.commit()
    affected = cur.rowcount
    conn.close()
    return affected > 0

if __name__ == '__main__':
    conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
    cur = conn.cursor()
    cur.execute("""
        SELECT stock_code, stock_name, listing_date 
        FROM stock_ipo 
        WHERE allotment_rate IS NULL 
        AND listing_date IS NOT NULL 
        AND listing_date <= CURRENT_DATE
        ORDER BY listing_date DESC
        LIMIT 20
    """)
    ipos = cur.fetchall()
    conn.close()
    
    print(f'Processing {len(ipos)} IPOs...\n')
    
    success = 0
    failed = 0
    
    for code, name, date in ipos:
        print(f'Scraping {code} {name} ({date})...')
        data = scrape_ipo_detail(code)
        
        if data.get('allotment_rate') or data.get('oversubscription_ratio'):
            print(f'  -> allotment_rate={data.get("allotment_rate")}, oversubscription={data.get("oversubscription_ratio")}, entry_fee={data.get("entry_fee")}')
            updated = update_db(data)
            if updated:
                success += 1
                print(f'  -> DB updated!')
            else:
                print(f'  -> DB update failed')
        else:
            print(f'  -> No allocation data found')
            failed += 1
        
        time.sleep(1)  # Be polite
    
    print(f'\nDone: {success} updated, {failed} no data')
