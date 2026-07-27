#!/usr/bin/env python3
"""港股IPO数据补全脚本 - 精确解析AASTOCKS表格"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False

import psycopg2
from bs4 import BeautifulSoup
import time
import sys
import re
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
    text = text.strip().replace(',', '').replace('%', '').replace('亿', '').replace('万', '').replace('千', '').replace('十万', '')
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
    except Exception as e:
        print(f"  请求失败: {e}")
        return {}
    
    if resp.status_code != 200:
        return {}
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    tables = soup.find_all('table')
    result = {}
    
    for t_idx, table in enumerate(tables):
        rows = table.find_all('tr')
        if len(rows) < 2:
            continue
        
        # 提取所有文本用于分析
        all_text = ' '.join([td.get_text(strip=True) for td in table.find_all('td')])
        
        # === Table 21-22: 招股日期表格 ===
        # 表头通常包含：招股日期、定价日期、公布售股结果日期、退票寄发日期、上市日期
        if '招股日期' in all_text and '定价日期' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for i, cell in enumerate(cells):
                    cell_clean = re.sub(r'\s+', ' ', cell)
                    if re.search(r'^招股日期$', cell_clean):
                        # 找同行的日期范围
                        date_range = re.search(r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})\s*-\s*(\d{4}[/-]\d{1,2}[/-]\d{1,2})', cell)
                        if date_range:
                            result['subscription_start'] = parse_date(date_range.group(1))
                            result['subscription_end'] = parse_date(date_range.group(2))
                    elif re.search(r'^定价日期$', cell_clean):
                        if i+1 < len(cells):
                            result['pricing_date'] = parse_date(cells[i+1])
                    elif re.search(r'^公布售股结果日期$', cell_clean):
                        if i+1 < len(cells):
                            result['allotment_date'] = parse_date(cells[i+1])
                    elif re.search(r'^上市日期$', cell_clean) and '退票' not in cells[i]:
                        if i+1 < len(cells):
                            result['listing_date_2'] = parse_date(cells[i+1])
        
        # === 每手股数、招股价、入场费 (Table 24类型) ===
        if '每手股数' in all_text and '招股价' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 2:
                    key = re.sub(r'\s+', '', cells[0])
                    val = cells[1].strip()
                    if '每手股数' in key:
                        result['lot_size'] = parse_num(val)
                    elif '招股价' in key:
                        result['issue_price_2'] = parse_num(val)
                    elif '入场费' in key:
                        result['entry_fee_2'] = parse_num(val.replace(',', ''))
        
        # === 行业 ===
        if re.search(r'^行业$', all_text) and len(rows) > 1:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 2 and re.search(r'^行业$', cells[0]):
                    result['sector'] = cells[1].strip()
        
        # === 保荐人 - 寻找包含保荐人公司名称的行 ===
        # 保荐人通常在类似 "招银国际融资有限公司、中银国际亚洲有限公司" 这样的文本中
        if '保荐人' in all_text and '公司' not in all_text:
            # 可能是保荐人比较表格
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for cell in cells:
                    if '有限公司' in cell and len(cell) > 10 and len(cell) < 300:
                        result['sponsor'] = cell.strip()
                        break
        
        # === 公开发售比例、国际配售比例 ===
        if '公开发售' in all_text and '国际' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for i, cell in enumerate(cells):
                    if '公开发售' in cell and i+1 < len(cells):
                        val = cells[i+1].strip()
                        if '%' in val or parse_num(val):
                            result['public_offering_ratio'] = parse_num(val.replace('%', ''))
                    if '国际' in cell and '配售' in cell and i+1 < len(cells):
                        val = cells[i+1].strip()
                        if '%' in val or parse_num(val):
                            result['international_placement_ratio'] = parse_num(val.replace('%', ''))
        
        # === 募资金额 ===
        if '集资' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for i, cell in enumerate(cells):
                    if '集资' in cell and i+1 < len(cells):
                        val = cells[i+1]
                        # 解析如 "5.67千万" 或 "8.5亿"
                        if '亿' in val:
                            result['fundraising_amount'] = parse_num(val.replace('亿', '')) * 100000000
                        elif '千万' in val:
                            result['fundraising_amount'] = parse_num(val.replace('千万', '')) * 10000000
                        elif '百万' in val:
                            result['fundraising_amount'] = parse_num(val.replace('百万', '')) * 1000000
    
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
        'fundraising_amount': 'fundraising_amount',
        'sponsor': 'sponsor',
        'public_offering_ratio': 'public_offering_ratio',
        'international_placement_ratio': 'international_placement_ratio',
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
    print("开始补全IPO数据...")
    
    # 先测试几个
    test_codes = ['00664', '03625', '06636', '01021']
    for code in test_codes:
        cur.execute("SELECT stock_name FROM stock_ipo WHERE stock_code = %s", (code,))
        row = cur.fetchone()
        name = row[0] if row else 'Unknown'
        print(f"\n测试股票: {code} {name}")
        data = scrape_ipo_detail(code)
        print(f"  爬取结果: {data}")
        if data:
            update_ipo(code, data)
    
    conn.commit()
    
    # 检查补全情况
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(sector) as has_sector,
            COUNT(subscription_start) as has_sub_start,
            COUNT(issue_price) as has_price,
            COUNT(sponsor) as has_sponsor
        FROM stock_ipo WHERE listing_date >= '2025-01-01'
    """)
    r = cur.fetchone()
    print(f"\n数据完整性: 总={r[0]}, 行业={r[1]}, 招股开始={r[2]}, 发行价={r[3]}, 保荐人={r[4]}")

if __name__ == '__main__':
    main()