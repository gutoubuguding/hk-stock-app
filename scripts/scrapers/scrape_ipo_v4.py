#!/usr/bin/env python3
"""港股IPO数据补全脚本 v4 - 精确解析表格"""
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
    
    for t_idx, table in enumerate(tables):
        rows = table.find_all('tr')
        if len(rows) < 2:
            continue
        
        all_text = ' '.join([td.get_text(strip=True) for td in table.find_all('td')])
        
        # === Table 20/21/22: IPO招股日程和公司资料 ===
        if '招股日期' in all_text and '定价日期' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) < 2:
                    continue
                
                # Cell 0 is label, Cell 1 is value
                label = cells[0].strip()
                value = cells[1].strip() if len(cells) > 1 else ''
                
                if label == '招股日期':
                    # value like "2026/03/23 - 2026/03/26"
                    m = re.search(r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})\s*-\s*(\d{4}[/-]\d{1,2}[/-]\d{1,2})', value)
                    if m:
                        result['subscription_start'] = parse_date(m.group(1))
                        result['subscription_end'] = parse_date(m.group(2))
                elif label == '定价日期':
                    result['pricing_date'] = parse_date(value)
                elif label == '公布售股结果日期':
                    result['allotment_date'] = parse_date(value)
                elif label == '上市日期':
                    result['listing_date_2'] = parse_date(value)
                elif label == '行业' and value:
                    result['sector'] = value
        
        # === Table 24: 股票数据 (每手股数、招股价、保荐人) ===
        if '每手股数' in all_text and '招股价' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) < 2:
                    continue
                
                label = cells[0].strip()
                value = cells[1].strip()
                
                if label == '每手股数':
                    result['lot_size'] = parse_num(value)
                elif label == '招股价':
                    result['issue_price_2'] = parse_num(value)
                elif label == '保荐人':
                    result['sponsor'] = value
                elif label == '香港配售股份数目':
                    # Parse "1111000(15.00%)" for public offering ratio
                    m = re.search(r'\((\d+\.?\d*)%\)', value)
                    if m:
                        result['public_offering_ratio'] = parse_num(m.group(1))
        
        # === 超购倍数、中签率 (Table 29) ===
        if '超额倍数' in all_text and '一手中签率' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 4:
                    # 通常格式: 公司名, 超额倍数, 一手中签率, 稳中一手
                    over = parse_num(cells[1]) if len(cells) > 1 else None
                    rate = parse_num(cells[2]) if len(cells) > 2 else None
                    if over:
                        result['oversubscription_ratio'] = over
                    if rate:
                        result['allotment_rate'] = rate
        
        # === 首日表现 (Table 31) ===
        if '首日表現' in all_text or '首日表现' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for cell in cells:
                    m = re.search(r'([+-]?\d+\.?\d*)%', cell)
                    if m:
                        result['first_day_change_2'] = parse_num(m.group(1))
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
        'sponsor': 'sponsor',
        'public_offering_ratio': 'public_offering_ratio',
        'oversubscription_ratio': 'oversubscription_ratio',
        'allotment_rate': 'allotment_rate',
        'first_day_change_2': 'first_day_change',
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
    # 测试
    test_codes = ['00664', '03625', '06636', '01021', '02526']
    
    for code in test_codes:
        cur.execute("SELECT stock_name FROM stock_ipo WHERE stock_code = %s", (code,))
        row = cur.fetchone()
        name = row[0] if row else 'Unknown'
        print(f"\n处理: {code} {name}")
        
        data = scrape_ipo_detail(code)
        print(f"  数据: {data}")
        
        if data:
            update_ipo(code, data)
            print(f"  已更新")
    
    conn.commit()
    
    # 验证
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(sector) as has_sector,
            COUNT(subscription_start) as has_sub,
            COUNT(lot_size) as has_lot,
            COUNT(issue_price) as has_price,
            COUNT(sponsor) as has_sponsor
        FROM stock_ipo WHERE listing_date >= '2025-01-01'
    """)
    r = cur.fetchone()
    print(f"\n完整性: 总={r[0]}, 行业={r[1]}, 招股开始={r[2]}, 每手={r[3]}, 发行价={r[4]}, 保荐人={r[5]}")

if __name__ == '__main__':
    main()