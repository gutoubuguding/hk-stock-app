#!/usr/bin/env python3
"""
港股IPO数据补全脚本
从AASTOCKS爬取完整的IPO数据字段
"""
import os
os.environ['NO_PROXY'] = '*'
import requests
requests.sessions.Session.trust_env = False

import psycopg2
from bs4 import BeautifulSoup
import time
import sys
import re
import json
sys.stdout.reconfigure(encoding='utf-8')

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'http://www.aastocks.com/',
}

conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

def parse_number(text):
    """解析数字，处理逗号、N/A等"""
    if not text or text == 'N/A' or text == '-':
        return None
    text = text.strip().replace(',', '').replace('%', '')
    try:
        return float(text)
    except:
        return None

def parse_date(text):
    """解析日期字符串 YYYY/MM/DD"""
    if not text or text == 'N/A':
        return None
    text = text.strip()
    # 匹配 YYYY/MM/DD 或 YYYY-MM-DD
    m = re.search(r'(\d{4})[/-](\d{1,2})[/-](\d{1,2})', text)
    if m:
        return f"{m.group(1)}-{m.group(2).zfill(2)}-{m.group(3).zfill(2)}"
    return None

def scrape_ipo_detail(stock_code):
    """爬取单个股票的IPO详情页"""
    url = f'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol={stock_code}#info'
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        resp.encoding = 'utf-8'
    except:
        return None
    
    if resp.status_code != 200:
        return None
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    tables = soup.find_all('table')
    
    result = {}
    
    # Table 20: IPO招股日程表 (公司名称、行业、招股价、每手股数、入场费、招股截止日、暗盘日期、上市日期)
    for table in tables:
        rows = table.find_all('tr')
        if len(rows) < 2:
            continue
        
        all_text = ' '.join([td.get_text(strip=True) for td in table.find_all('td')])
        
        # 提取每手股数和招股价
        if '每手股数' in all_text and '招股价' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 2:
                    key = cells[0].strip()
                    val = cells[1].strip()
                    if '每手股数' == key:
                        result['lot_size'] = parse_number(val)
                    elif '招股价' == key:
                        result['issue_price_2'] = parse_number(val)
        
        # Table 21-22: 招股日期、定价日期、公布结果日期、退票日期、上市日期
        if '招股日期' in all_text and '定价日期' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for cell in cells:
                    if '招股日期' in cell and '-' in cell:
                        # 格式: 2026/03/23 - 2026/03/26
                        m = re.search(r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})\s*-\s*(\d{4}[/-]\d{1,2}[/-]\d{1,2})', cell)
                        if m:
                            result['subscription_start'] = parse_date(m.group(1))
                            result['subscription_end'] = parse_date(m.group(2))
                    elif '定价日期' in cell:
                        m = re.search(r'定价日期\s*[:：]?\s*(\d{4}[/-]\d{1,2}[/-]\d{1,2})', cell)
                        if m:
                            result['pricing_date'] = parse_date(m.group(1))
                    elif '公布售股结果' in cell:
                        m = re.search(r'公布售股结果[日期期]*\s*[:：]?\s*(\d{4}[/-]\d{1,2}[/-]\d{1,2})', cell)
                        if m:
                            result['allotment_date'] = parse_date(m.group(1))
                    elif '上市日期' in cell and '退票' not in cell:
                        m = re.search(r'上市日期\s*[:：]?\s*(\d{4}[/-]\d{1,2}[/-]\d{1,2})', cell)
                        if m:
                            result['listing_date_2'] = parse_date(m.group(1))
        
        # 提取行业
        if '行业' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 2 and cells[0].strip() == '行业':
                    result['sector'] = cells[1].strip()
        
        # 提取保荐人
        if '保荐人' in all_text and len(rows) > 1:
            # 保荐人在一个单独的区块
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 2 and cells[0].strip() == '保荐人':
                    result['sponsor'] = cells[1].strip()
        
        # 提取每手入场费
        if '入场费' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 2 and cells[0].strip() == '入场费':
                    val = cells[1].strip().replace(',', '')
                    result['entry_fee_2'] = parse_number(val)
        
        # 提取集资规模/募资金额
        if '集资' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for i, cell in enumerate(cells):
                    if '集资' in cell and i+1 < len(cells):
                        val = cells[i+1].strip().replace(',', '').replace('亿', '')
                        if '千万' in val:
                            result['fundraising_amount'] = parse_number(val.replace('千万', '')) * 10000000
                        elif '百万' in val:
                            result['fundraising_amount'] = parse_number(val.replace('百万', '')) * 1000000
                        elif '万' in val:
                            result['fundraising_amount'] = parse_number(val.replace('万', '')) * 10000
    
    # 从其他表格补充数据
    for table in tables:
        rows = table.find_all('tr')
        all_text = ' '.join([td.get_text(strip=True) for td in table.find_all('td')])
        
        # 超购倍数、中签率、稳中一手
        if '超额倍数' in all_text and '一手中签率' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 3:
                    # 找包含数字的行 (公司名称、超额倍数、一手中签率、稳中一手)
                    for cell in cells:
                        if parse_number(cell) is not None:
                            idx = cells.index(cell)
                            # 可能一行有多个字段
                            if idx == 0 and len(cells) >= 2:
                                # 超额倍数
                                result['oversubscription_ratio'] = parse_number(cells[1]) if parse_number(cells[1]) else result.get('oversubscription_ratio')
                            if idx == 2 and len(cells) >= 3:
                                result['allotment_rate'] = parse_number(cells[2])
        
        # 保荐人比较表
        if '保荐人比较' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 1 and '公司' not in cells[0] and cells[0].strip() and not parse_number(cells[0]):
                    # 保荐人行
                    sponsor_text = cells[0].strip()
                    if '保荐人' not in sponsor_text and len(sponsor_text) > 5:
                        result['sponsor'] = sponsor_text
        
        # 首日表现
        if '首日表現' in all_text or '首日表现' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for cell in cells:
                    m = re.search(r'([+-]?\d+\.?\d*)%', cell)
                    if m and '首日' in all_text:
                        result['first_day_change_2'] = parse_number(m.group(1))
                        break
    
    return result

def update_stock_ipo(stock_code, data):
    """更新数据库中的IPO记录"""
    if not data:
        return False
    
    updates = []
    params = []
    
    fields_map = {
        'sector': 'sector',
        'subscription_start': 'subscription_start',
        'subscription_end': 'subscription_end',
        'pricing_date': 'pricing_date',
        'allotment_date': 'allotment_date',
        'sponsor': 'sponsor',
        'lot_size': 'lot_size',
        'issue_price_2': 'issue_price',
        'entry_fee_2': 'entry_fee',
        'fundraising_amount': 'fundraising_amount',
        'oversubscription_ratio': 'oversubscription_ratio',
        'allotment_rate': 'allotment_rate',
        'first_day_change_2': 'first_day_change',
    }
    
    for src, dst in fields_map.items():
        if src in data and data[src] is not None:
            updates.append(f"{dst} = %s")
            params.append(data[src])
    
    if not updates:
        return False
    
    params.append(stock_code)
    sql = f"UPDATE stock_ipo SET {', '.join(updates)}, updated_at = NOW() WHERE stock_code = %s"
    
    try:
        cur.execute(sql, params)
        return cur.rowcount > 0
    except Exception as e:
        print(f"Update error for {stock_code}: {e}")
        return False

def main():
    # 获取所有需要补全的股票
    cur.execute("""
        SELECT stock_code, stock_name, listing_date 
        FROM stock_ipo 
        WHERE listing_date >= '2025-01-01'
        AND (sector IS NULL OR sponsor IS NULL OR first_day_change IS NULL 
             OR issue_price IS NULL OR subscription_start IS NULL)
        ORDER BY listing_date DESC
    """)
    stocks = cur.fetchall()
    print(f"需要补全的股票数量: {len(stocks)}")
    
    if not stocks:
        print("没有需要补全的股票")
        return
    
    success = 0
    failed = 0
    
    for stock_code, stock_name, listing_date in stocks:
        print(f"处理: {stock_code} {stock_name}")
        
        data = scrape_ipo_detail(stock_code)
        if data:
            updated = update_stock_ipo(stock_code, data)
            if updated:
                success += 1
                print(f"  ✓ 更新成功: {list(data.keys())}")
            else:
                failed += 1
                print(f"  ✗ 更新失败（无新数据）")
        else:
            failed += 1
            print(f"  ✗ 爬取失败")
        
        time.sleep(0.5)  # 避免请求过快
    
    conn.commit()
    print(f"\n补全完成: 成功={success}, 失败={failed}")
    
    # 验证结果
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(sector) as has_sector,
            COUNT(sponsor) as has_sponsor,
            COUNT(issue_price) as has_price,
            COUNT(first_day_change) as has_change
        FROM stock_ipo WHERE listing_date >= '2025-01-01'
    """)
    row = cur.fetchone()
    print(f"\n数据完整性: 总数={row[0]}, 行业={row[1]}, 保荐人={row[2]}, 发行价={row[3]}, 首日涨跌幅={row[4]}")

if __name__ == '__main__':
    main()