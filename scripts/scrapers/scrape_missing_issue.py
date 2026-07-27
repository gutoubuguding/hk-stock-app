#!/usr/bin/env python3
"""从AASTOCKS获取缺失发行价的股票数据"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False

import psycopg2
from bs4 import BeautifulSoup
import time
import re
import sys
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'http://www.aastocks.com/',
}

conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

def parse_num(text):
    if not text or text in ('N/A', '-', ''):
        return None
    text = text.strip().replace(',', '').replace('%', '')
    try:
        return float(text)
    except:
        return None

def scrape_issue_price(stock_code):
    url = f'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol={stock_code}#info'
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
    except:
        return {}
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    tables = soup.find_all('table')
    result = {}
    
    for table in tables:
        rows = table.find_all('tr')
        all_text = ' '.join([td.get_text(strip=True) for td in table.find_all('td')])
        
        if '每手股数' in all_text and '招股价' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 2:
                    label = cells[0].strip()
                    value = cells[1].strip()
                    if label == '招股价':
                        result['issue_price'] = parse_num(value)
                    elif label == '每手股数':
                        result['lot_size'] = parse_num(value)
                    elif label == '入场费':
                        result['entry_fee'] = parse_num(value.replace(',', ''))
                    elif label == '保荐人':
                        result['sponsor'] = value
        
        if '招股日期' in all_text and '定价日期' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 2:
                    label = cells[0].strip()
                    value = cells[1].strip()
                    if label == '行业' and value:
                        result['sector'] = value
    
    return result

def main():
    # 获取缺失发行价的股票
    cur.execute("SELECT stock_code, stock_name FROM stock_ipo WHERE listing_date >= '2025-01-01' AND issue_price IS NULL ORDER BY listing_date")
    stocks = cur.fetchall()
    print(f"需要补全发行价的股票: {len(stocks)}")
    
    success = 0
    for code, name in stocks:
        print(f"[{code}] {name}")
        data = scrape_issue_price(code)
        
        if 'issue_price' in data and data['issue_price']:
            cur.execute("""
                UPDATE stock_ipo 
                SET issue_price = %s, lot_size = COALESCE(%s, lot_size), 
                    entry_fee = COALESCE(%s, entry_fee),
                    sponsor = COALESCE(%s, sponsor),
                    sector = COALESCE(%s, sector),
                    updated_at = NOW()
                WHERE stock_code = %s
            """, (data['issue_price'], data.get('lot_size'), data.get('entry_fee'), data.get('sponsor'), data.get('sector'), code))
            print(f"  -> 发行价={data['issue_price']}, 每手={data.get('lot_size')}, 保荐人={str(data.get('sponsor'))[:30] if data.get('sponsor') else 'N/A'}")
            success += 1
        else:
            print(f"  -> 未获取到发行价")
        
        time.sleep(0.3)
    
    conn.commit()
    print(f"\n完成: 成功={success}/{len(stocks)}")

if __name__ == '__main__':
    main()