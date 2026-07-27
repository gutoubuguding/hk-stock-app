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

def get_ipo_list():
    """Get list of IPOs that have listed but don't have allotment data yet"""
    conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
    cur = conn.cursor()
    cur.execute("""
        SELECT stock_code, stock_name, listing_date 
        FROM stock_ipo 
        WHERE allotment_rate IS NULL 
        AND listing_date IS NOT NULL 
        AND listing_date <= CURRENT_DATE
        ORDER BY listing_date DESC
        LIMIT 50
    """)
    rows = cur.fetchall()
    conn.close()
    return rows

def scrape_ipo_allocation(stock_code):
    """Scrape allocation result for a specific stock from AASTOCKS"""
    code = stock_code.replace('HK.', '').replace('.', '').zfill(5)
    url = f'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol={code}'
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        result = {}
        
        # Find all tables and look for allocation data
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                
                # Look for oversubscription ratio (认购倍数)
                for i, cell in enumerate(cells):
                    if '倍数' in cell or '倍' in cell:
                        if i+1 < len(cells):
                            val = cells[i+1].replace(',', '')
                            try:
                                result['oversubscription_ratio'] = float(val)
                            except:
                                pass
                    
                    # Look for allotment rate (中签率)
                    if '中签' in cell or '一手' in cell and '%' in str(cells):
                        for c in cells:
                            if '%' in c and not 'N/A' in c:
                                num = c.replace('%', '').replace('+', '').strip()
                                try:
                                    result['allotment_rate'] = float(num)
                                    break
                                except:
                                    pass
                    
                    # Look for entry fee (入场费)
                    if '入场' in cell and i+1 < len(cells):
                        val = cells[i+1].replace(',', '').replace('港', '').strip()
                        try:
                            result['entry_fee'] = float(val)
                        except:
                            pass
        
        # Also try to extract from specific div/span elements
        # Look for the allocation result section
        for div in soup.find_all(['div', 'span'], class_=True):
            text = div.get_text(strip=True)
            if '中签率' in text or '配发结果' in text:
                # Try to extract percentage
                match = re.search(r'(\d+\.?\d*)%', text)
                if match:
                    result['allotment_rate'] = float(match.group(1))
        
        return result
    except Exception as e:
        print(f'  Error scraping {code}: {e}')
        return {}

def scrape_main_ipo_page():
    """Scrape the main IPO listing page which has overview data"""
    url = 'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol=01021'
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # Parse Table 30 which we know has the data
    tables = soup.find_all('table')
    if len(tables) > 30:
        table = tables[30]
        rows = table.find_all('tr')
        
        print(f'Table 30 rows: {len(rows)}')
        all_data = []
        for row in rows:
            cells = []
            for td in row.find_all(['td', 'th']):
                text = td.get_text(strip=True)
                # Try to get proper Chinese text
                cells.append(text)
            if cells:
                all_data.append(cells)
        
        return all_data
    return []

def update_db(stock_code, allotment_rate, oversubscription_ratio=None, entry_fee=None):
    """Update the IPO record with allocation data"""
    conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
    cur = conn.cursor()
    
    updates = ['allotment_rate = %s']
    params = [allotment_rate]
    
    if oversubscription_ratio is not None:
        updates.append('oversubscription_ratio = %s')
        params.append(oversubscription_ratio)
    
    if entry_fee is not None:
        updates.append('entry_fee = %s')
        params.append(entry_fee)
    
    params.append(stock_code)
    
    sql = f"UPDATE stock_ipo SET {', '.join(updates)} WHERE stock_code = %s"
    cur.execute(sql, params)
    conn.commit()
    affected = cur.rowcount
    conn.close()
    return affected

if __name__ == '__main__':
    # First, scrape the main page to get overview data
    print('=== Scraping main IPO page ===')
    data = scrape_main_ipo_page()
    
    # Build a mapping from stock code to data
    ipo_mapping = {}
    for row in data:
        if len(row) >= 3:
            # Try to find stock code in the row
            for cell in row:
                # Look for stock code patterns
                match = re.search(r'(\d{5})\.HK', cell)
                if match:
                    code = match.group(1).lstrip('0') or '0'
                    code = 'HK.' + code.zfill(5)
                    ipo_mapping[code] = row
                    break
    
    print(f'Found {len(ipo_mapping)} IPOs with data from main page')
    
    # Also check Table 30 specifically
    url = 'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol=01021'
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    soup = BeautifulSoup(resp.text, 'html.parser')
    tables = soup.find_all('table')
    
    # Table 30 - 认购倍数/一手中签率
    if len(tables) > 30:
        table = tables[30]
        rows = table.find_all('tr')
        print(f'\n=== Table 30 (Allocation Summary) - {len(rows)} rows ===')
        
        # Parse header
        header_cells = [td.get_text(strip=True) for td in rows[0].find_all(['td', 'th'])]
        print(f'Header: {header_cells}')
        
        # Parse data rows
        allocation_data = []
        for row in rows[1:]:
            cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
            if cells and len(cells) >= 3:
                print(f'Row: {cells}')
                allocation_data.append(cells)
    
    # Table 32 - 承销商数据
    if len(tables) > 32:
        table = tables[32]
        rows = table.find_all('tr')
        print(f'\n=== Table 32 ===')
        for row in rows[:5]:
            cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
            if cells:
                print(f'Row: {cells}')
    
    # Now get existing IPOs from database and try to match
    print('\n=== Getting IPOs from database ===')
    conn = psycopg2.connect(host='localhost', dbname='hk_stock', user='postgres', password='pc20050218')
    cur = conn.cursor()
    cur.execute("""
        SELECT stock_code, stock_name, listing_date, allotment_rate, oversubscription_ratio
        FROM stock_ipo 
        WHERE listing_date IS NOT NULL 
        AND listing_date <= CURRENT_DATE
        ORDER BY listing_date DESC
        LIMIT 30
    """)
    db_ipos = cur.fetchall()
    conn.close()
    
    print(f'Database has {len(db_ipos)} listed IPOs (recent 30):')
    for code, name, date, rate, ratio in db_ipos:
        print(f'  {code} {name} ({date}) - rate:{rate} ratio:{ratio}')
