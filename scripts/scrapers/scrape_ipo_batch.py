#!/usr/bin/env python3
"""港股IPO数据补全脚本 v5 - 批量处理170只股票"""
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
        
        # Table 21/22: 招股日程
        if '招股日期' in all_text and '定价日期' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) < 2:
                    continue
                
                label = cells[0].strip()
                value = cells[1].strip()
                
                if label == '招股日期':
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
        
        # Table 24: 每手股数、招股价、保荐人、配售比例
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
                    m = re.search(r'\((\d+\.?\d*)%\)', value)
                    if m:
                        result['public_offering_ratio'] = parse_num(m.group(1))
        
        # 超购倍数、中签率 - 从Table 29 (最近新股中签率)
        if '超额倍数' in all_text and '一手中签率' in all_text and '公司名称' not in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) >= 4:
                    over = parse_num(cells[1]) if len(cells) > 1 else None
                    rate = parse_num(cells[2]) if len(cells) > 2 else None
                    if over is not None:
                        result['oversubscription_ratio'] = over
                    if rate is not None:
                        result['allotment_rate'] = rate
        
        # 首日表现 - Table 31
        if ('首日表現' in all_text or '首日表现' in all_text) and '保荐人' not in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                for cell in cells:
                    m = re.search(r'([+-]?\d+\.?\d*)%', cell)
                    if m and '首日' in all_text:
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
        return cur.rowcount >= 0
    except Exception as e:
        print(f"  DB错误: {e}")
        return False

def main():
    # 获取所有需要补全的股票
    cur.execute("""
        SELECT stock_code, stock_name 
        FROM stock_ipo 
        WHERE listing_date >= '2025-01-01'
        AND (sector IS NULL OR sponsor IS NULL OR lot_size IS NULL)
        ORDER BY listing_date DESC
    """)
    stocks = cur.fetchall()
    total = len(stocks)
    print(f"需要补全的股票数量: {total}")
    
    if total == 0:
        print("没有需要补全的股票")
        return
    
    success = 0
    failed = 0
    skip = 0
    
    for idx, (code, name) in enumerate(stocks):
        print(f"[{idx+1}/{total}] 处理: {code} {name}")
        
        data = scrape_ipo_detail(code)
        
        if not data:
            failed += 1
            print(f"  无数据")
            time.sleep(0.3)
            continue
        
        updated = update_ipo(code, data)
        if updated:
            success += 1
            filled = [k for k in data if data[k] is not None]
            print(f"  成功: {filled}")
        else:
            skip += 1
            print(f"  跳过")
        
        time.sleep(0.3)  # 避免被限流
    
    conn.commit()
    print(f"\n=== 补全完成 ===")
    print(f"成功: {success}, 跳过: {skip}, 失败: {failed}")
    
    # 最终验证
    cur.execute("""
        SELECT 
            COUNT(*) as total,
            COUNT(sector) as has_sector,
            COUNT(subscription_start) as has_sub,
            COUNT(lot_size) as has_lot,
            COUNT(issue_price) as has_price,
            COUNT(sponsor) as has_sponsor,
            COUNT(oversubscription_ratio) as has_over,
            COUNT(allotment_rate) as has_rate
        FROM stock_ipo WHERE listing_date >= '2025-01-01'
    """)
    r = cur.fetchone()
    print(f"\n数据完整性:")
    print(f"  总数: {r[0]}")
    print(f"  行业(sector): {r[1]}")
    print(f"  招股开始(subscription_start): {r[2]}")
    print(f"  每手股数(lot_size): {r[3]}")
    print(f"  发行价(issue_price): {r[4]}")
    print(f"  保荐人(sponsor): {r[5]}")
    print(f"  超购倍数(oversubscription_ratio): {r[6]}")
    print(f"  中签率(allotment_rate): {r[7]}")

if __name__ == '__main__':
    main()