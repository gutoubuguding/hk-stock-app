import requests
from bs4 import BeautifulSoup
import psycopg2
import json
import re
import time

def scrape_aastocks_ipo():
    """Scrape IPO data from AASTOCKS"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    # AASTOCKS IPO page - list of recent IPOs with allocation results
    url = 'http://www.aastocks.com/sc/ipo/listedipo.aspx'
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        print(f'Status: {resp.status_code}')
        print(f'Content length: {len(resp.text)}')
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        
        # Find the IPO table
        tables = soup.find_all('table')
        print(f'Found {len(tables)} tables')
        
        # Try to find data in the page
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if len(rows) > 2:
                print(f'\nTable {i}: {len(rows)} rows')
                # Print first row as header
                first_row = rows[0]
                headers_text = [td.get_text(strip=True) for td in first_row.find_all(['td', 'th'])]
                print(f'  Headers: {headers_text[:10]}')
                
                # Print a few data rows
                for row in rows[1:4]:
                    cells = [td.get_text(strip=True) for td in row.find_all('td')]
                    if cells:
                        print(f'  Row: {cells[:10]}')
        
        return soup
    except Exception as e:
        print(f'Error: {e}')
        return None

def try_hkex_ipo():
    """Try HKEX API for IPO data"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    }
    
    # Try the HKEX API endpoint
    url = 'https://www1.hkexnews.hk/ncms/json/eds/activestock_c.json'
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        print(f'HKEX API status: {resp.status_code}')
        if resp.status_code == 200:
            data = resp.json()
            print(f'Keys: {list(data.keys())[:10]}')
    except Exception as e:
        print(f'HKEX Error: {e}')

def try_etnet_ipo():
    """Try etnet for IPO data"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    }
    
    url = 'https://www.etnet.com.hk/www/sc/stocks/ci_ipo_list.php'
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
        print(f'etnet status: {resp.status_code}, length: {len(resp.text)}')
        
        soup = BeautifulSoup(resp.text, 'html.parser')
        tables = soup.find_all('table')
        print(f'Found {len(tables)} tables')
        
        for i, table in enumerate(tables):
            rows = table.find_all('tr')
            if len(rows) > 3:
                print(f'\netnet Table {i}: {len(rows)} rows')
                for row in rows[:5]:
                    cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                    if cells and len(cells) > 2:
                        print(f'  {cells[:12]}')
        
        return soup
    except Exception as e:
        print(f'etnet Error: {e}')
        return None

if __name__ == '__main__':
    print('=== Trying AASTOCKS ===')
    scrape_aastocks_ipo()
    
    print('\n=== Trying etnet ===')
    try_etnet_ipo()
