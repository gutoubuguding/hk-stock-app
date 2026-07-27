#!/usr/bin/env python3
"""补全剩余IPO字段: 入场费、公开发售比例、基石投资者等"""
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

def scrape_remaining_fields(stock_code):
    """从AASTOCKS获取补充字段"""
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
        
        # 入场费 - 通常在 Table 24 或 Table 20
        if '入场费' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for i, cell in enumerate(cells):
                    if '入场费' in cell:
                        # 找同行下一列
                        for j in range(i+1, len(cells)):
                            val = cells[j].strip().replace(',', '')
                            if parse_num(val):
                                result['entry_fee'] = parse_num(val)
                                break
        
        # 公开发售比例 - 香港配售股份数目 (15.00%)
        if '香港配售股份数目' in all_text or '公开发售' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for cell in cells:
                    # 匹配 "1111000(15.00%)" 格式
                    m = re.search(r'(\d+)\s*\((\d+\.?\d*)%\)', cell)
                    if m:
                        result['public_offering_ratio'] = parse_num(m.group(2))
                        break
        
        # 基石投资者 - 可能在其他表格
        if '基石' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for cell in cells:
                    if '基石' in cell and len(cell) > 5:
                        result['cornerstone_investor'] = cell.strip()
                        break
        
        # 募资金额 - 集资规模
        if '集资' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for cell in cells:
                    if '集资' in cell:
                        # 格式如 "5.67千万" 或 "8.5亿"
                        val = cell.replace('集资', '').strip()
                        if '亿' in val:
                            result['fundraising_amount'] = parse_num(val.replace('亿', '')) * 100000000
                        elif '千万' in val:
                            result['fundraising_amount'] = parse_num(val.replace('千万', '')) * 10000000
                        elif '百万' in val:
                            result['fundraising_amount'] = parse_num(val.replace('百万', '')) * 1000000
                        break
        
        # 发行市盈率
        if '发行市盈率' in all_text or '市盈率' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for i, cell in enumerate(cells):
                    if '发行市盈率' in cell or ('市盈率' in cell and '行业' not in cell):
                        for j in range(i+1, len(cells)):
                            if parse_num(cells[j]):
                                result['issue_pe'] = parse_num(cells[j])
                                break
    
    return result

def update_remaining(code, data):
    if not data:
        return False
    
    updates = []
    params = []
    
    for field in ['entry_fee', 'public_offering_ratio', 'cornerstone_investor', 
                  'fundraising_amount', 'issue_pe']:
        if field in data and data[field] is not None:
            updates.append(f"{field} = %s")
            params.append(data[field])
    
    if not updates:
        return False
    
    params.append(code)
    sql = f"UPDATE stock_ipo SET {', '.join(updates)}, updated_at = NOW() WHERE stock_code = %s"
    
    try:
        cur.execute(sql, params)
        return cur.rowcount >= 0
    except Exception as e:
        print(f"  DB错误: {e}")
        return False

def main():
    # 找出缺失这些字段的股票
    cur.execute("""
        SELECT stock_code, stock_name 
        FROM stock_ipo 
        WHERE listing_date >= '2025-01-01'
        AND (entry_fee IS NULL OR public_offering_ratio IS NULL OR cornerstone_investor IS NULL)
        ORDER BY listing_date DESC
    """)
    stocks = cur.fetchall()
    total = len(stocks)
    print(f"需要补全的股票: {total}")
    
    success = 0
    for idx, (code, name) in enumerate(stocks):
        print(f"[{idx+1}/{total}] {code} {name}")
        data = scrape_remaining_fields(code)
        if data:
            update_remaining(code, data)
            success += 1
            print(f"  成功: {list(data.keys())}")
        else:
            print(f"  无数据")
        time.sleep(0.3)
    
    conn.commit()
    
    # 验证
    cur.execute("""
        SELECT COUNT(entry_fee), COUNT(public_offering_ratio), 
               COUNT(cornerstone_investor), COUNT(fundraising_amount), COUNT(issue_pe)
        FROM stock_ipo WHERE listing_date >= '2025-01-01'
    """)
    r = cur.fetchone()
    print(f"\n入场费: {r[0]}, 公开发售比例: {r[1]}, 基石投资者: {r[2]}, 募资金额: {r[3]}, 发行PE: {r[4]}")

if __name__ == '__main__':
    main()