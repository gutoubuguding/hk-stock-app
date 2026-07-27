#!/usr/bin/env python3
"""港股IPO数据补全脚本 v3"""
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
    text = text.strip().replace(',', '').replace('%', '').replace('亿', '').replace('万', '').replace('千', '')
    try:
        return float(text)
    except:
        return None

def parse_date(text):
    if not text or text == 'N/A':
        return None
    m = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', text)
    if m:
        return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
    return None

def scrape_ipo_detail(stock_code):
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
        if len(rows) < 2:
            continue
        
        all_text = ' '.join([td.get_text(strip=True) for td in table.find_all('td')])
        
        # 招股日期、定价日期、公布结果日期、上市日期
        if '招股日期' in all_text and '定价日期' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for i, cell in enumerate(cells):
                    cell_clean = re.sub(r'\s+', ' ', cell)
                    if re.search(r'^招股日期$', cell_clean):
                        dr = re.search(r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})\s*-\s*(\d{4}[/-]\d{1,2}[/-]\d{1,2})', cell)
                        if dr:
                            result['subscription_start'] = parse_date(dr.group(1))
                            result['subscription_end'] = parse_date(dr.group(2))
                    elif re.search(r'^定价日期$', cell_clean) and i+1 < len(cells):
                        result['pricing_date'] = parse_date(cells[i+1])
                    elif re.search(r'^公布售股结果日期$', cell_clean) and i+1 < len(cells):
                        result['allotment_date'] = parse_date(cells[i+1])
                    elif re.search(r'^上市日期$', cell_clean) and '退票' not in cell and i+1 < len(cells):
                        result['listing_date_2'] = parse_date(cells[i+1])
        
        # 每手股数、招股价、入场费
        if '每手股数' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for i, cell in enumerate(cells):
                    if re.search(r'^每手股数$', re.sub(r'\s+', '', cell)) and i+1 < len(cells):
                        result['lot_size'] = parse_num(cells[i+1])
                    elif re.search(r'^招股价$', re.sub(r'\s+', '', cell)) and i+1 < len(cells):
                        result['issue_price_2'] = parse_num(cells[i+1])
                    elif re.search(r'^入场费$', re.sub(r'\s+', '', cell)) and i+1 < len(cells):
                        result['entry_fee_2'] = parse_num(cells[i+1].replace(',', ''))
        
        # 行业
        if re.search(r'\b行业\b', all_text) and len(rows) > 1:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 2 and re.search(r'^行业$', cells[0]):
                    result['sector'] = cells[1].strip()
        
        # 保荐人 - 包含"有限公司"的多公司字符串
        if '保荐人' in all_text and '公司' not in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for cell in cells:
                    if '有限公司' in cell and len(cell) > 10:
                        result['sponsor'] = cell.strip()
                        break
    
    return result

def update_ipo(code, data):
    if not data:
        return False
    
    updates = []
    params = []
    
    mapping = {
        'sector': 'sector',
        'subscription_start': 'subscription_start',
        'subscription_end': 'subscription_end',
        'pricing_date': 'pricing_date',
        'allotment_date': 'allotment_date',
        'listing_date_2': 'listing_date',
        'lot_size': 'lot_size',
        'issue_price_2': 'issue_price',
        'entry_fee_2': 'entry_fee',
        'sponsor': 'sponsor',
    }
    
    for src, dst in mapping.items():
        if src in data and data[src] is not None:
            updates.append(f"{dst} = %s")
            params.append(data[src])
    
    if not updates:
        return False
    
    params.append(code)
    sql = f"UPDATE stock_ipo SET {', '.join(updates)}, updated_at = NOW() WHERE stock_code = %s"
    
    try:
        cur.execute(sql, params)
        return cur.rowcount > 0
    except Exception as e:
        print(f"  DB错误: {e}")
        return False

def main():
    # 先测试几只
    test_codes = ['00664', '03625', '06636', '01021']
    
    for code in test_codes:
        cur.execute("SELECT stock_name FROM stock_ipo WHERE stock_code = %s", (code,))
        row = cur.fetchone()
        name = row[0] if row else 'Unknown'
        print(f"测试: {code} {name}")
        
        data = scrape_ipo_detail(code)
        print(f"  数据: {data}")
        
        if data:
            update_ipo(code, data)
            print(f"  已更新")
        print()
    
    conn.commit()
    
    # 验证
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(sector) as has_sector,
            COUNT(subscription_start) as has_sub,
            COUNT(issue_price) as has_price,
            COUNT(sponsor) as has_sponsor
        FROM stock_ipo WHERE listing_date >= '2025-01-01'
    """)
    r = cur.fetchone()
    print(f"完整性: 总={r[0]}, 行业={r[1]}, 招股={r[2]}, 发行价={r[3]}, 保荐人={r[4]}")

if __name__ == '__main__':
    main()