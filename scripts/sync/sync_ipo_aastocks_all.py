#!/usr/bin/env python3
"""从AAStocks爬取港股IPO历史数据（多页）"""
import sys
import os
os.environ['NO_PROXY'] = '*'

sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import psycopg2
import time

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': int(os.getenv('DB_PORT', '5432')),
    'database': os.getenv('DB_NAME', 'hk_stock'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'pc20050218')
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'http://www.aastocks.com/',
}

def parse_date(text):
    """解析日期 2026/07/10 格式"""
    if not text or text.strip() == '-':
        return None
    text = text.strip()
    try:
        return datetime.strptime(text, '%Y/%m/%d').date()
    except:
        return None

def parse_float(text):
    """解析浮点数"""
    if not text or text.strip() == '-':
        return None
    text = text.strip().replace(',', '')
    try:
        return float(text)
    except:
        return None

def scrape_page(page_num):
    """爬取一页IPO数据"""
    if page_num == 1:
        url = 'http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx'
    else:
        url = f'http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx?page={page_num}'
    
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.encoding = 'utf-8'
    
    if resp.status_code != 200:
        print(f'  页{page_num} 请求失败: {resp.status_code}')
        return []
    
    ipo_list = []
    
    # 使用BeautifulSoup解析HTML
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # 查找所有包含股票代码的链接
    # 格式: <a href="...">02249.HK</a>
    code_pattern = re.compile(r'^\d{5}\.HK$')
    
    for link in soup.find_all('a', string=code_pattern):
        code_text = link.get_text(strip=True)
        stock_code = code_text.replace('.HK', '')
        
        # 获取父行
        row = link.find_parent('tr')
        if not row:
            continue
        
        # 获取所有单元格
        cells = row.find_all('td')
        if len(cells) < 7:
            continue
        
        # 提取数据
        # 单元格顺序: 空 | 名称+代码 | 上市日期 | 每手股数 | 市值 | 招股价 | 上市价 | 超额倍数 | 稳中一手 | 中签率 | ...
        
        # 股票名称 - 在代码链接前面的链接中
        name_link = link.find_previous('a')
        stock_name = ''
        if name_link:
            stock_name = name_link.get_text(strip=True)
            # 去掉状态标记
            stock_name = re.sub(r'跌穿上市价$', '', stock_name).strip()
        
        # 上市日期 (cells[2])
        listing_date = None
        if len(cells) > 2:
            date_text = cells[2].get_text(strip=True)
            listing_date = parse_date(date_text)
        
        # 每手股数 (cells[3])
        lot_size = None
        if len(cells) > 3:
            lot_text = cells[3].get_text(strip=True).replace(',', '')
            try:
                lot_size = int(lot_text)
            except:
                pass
        
        # 招股价 (cells[5])
        issue_price = None
        if len(cells) > 5:
            issue_price = parse_float(cells[5].get_text(strip=True))
        
        # 上市价 (cells[6])
        list_price = None
        if len(cells) > 6:
            list_price = parse_float(cells[6].get_text(strip=True))
        
        # 超额倍数 (cells[7])
        oversubscription_ratio = None
        if len(cells) > 7:
            text = cells[7].get_text(strip=True).replace(',', '')
            if text and text != '-':
                try:
                    oversubscription_ratio = float(text)
                except:
                    pass
        
        # 中签率 (cells[9]) - 格式: "8.0%" 或 "-"
        allotment_rate = None
        if len(cells) > 9:
            text = cells[9].get_text(strip=True).replace('%', '')
            if text and text != '-':
                try:
                    allotment_rate = float(text)
                except:
                    pass
        
        if stock_code and listing_date:
            ipo_list.append({
                'stock_code': stock_code,
                'stock_name': stock_name,
                'listing_date': listing_date,
                'issue_price': issue_price,
                'list_price': list_price,
                'lot_size': lot_size,
                'oversubscription_ratio': oversubscription_ratio,
                'allotment_rate': allotment_rate,
            })
    
    return ipo_list

def main():
    print("从AAStocks爬取港股IPO历史数据...")
    
    all_ipos = []
    
    # 爬取前10页
    for page in range(1, 11):
        print(f'  爬取第{page}页...')
        try:
            ipos = scrape_page(page)
            all_ipos.extend(ipos)
            print(f'    获取到 {len(ipos)} 条记录')
            time.sleep(1)  # 避免请求过快
        except Exception as e:
            print(f'    错误: {e}')
    
    print(f'\n总共获取到 {len(all_ipos)} 条IPO记录')
    
    # 去重
    seen = set()
    unique_ipos = []
    for ipo in all_ipos:
        if ipo['stock_code'] not in seen:
            seen.add(ipo['stock_code'])
            unique_ipos.append(ipo)
    
    print(f'去重后: {len(unique_ipos)} 条记录')
    
    # 按日期排序
    unique_ipos.sort(key=lambda x: x['listing_date'] if x['listing_date'] else datetime(1900, 1, 1).date())
    
    # 打印前20条
    print('\n前20条记录:')
    for ipo in unique_ipos[:20]:
        print(f"  {ipo['stock_code']} {ipo['stock_name']} {ipo['listing_date']} 招股价:{ipo['issue_price']} 上市价:{ipo['list_price']} 每手:{ipo['lot_size']}")
    
    # 插入数据库
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    inserted = 0
    for ipo in unique_ipos:
        try:
            cur.execute("""
                INSERT INTO stock_ipo (stock_code, stock_name, listing_date, issue_price, lot_size, oversubscription_ratio, allotment_rate)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (stock_code) DO UPDATE SET
                    stock_name = EXCLUDED.stock_name,
                    listing_date = COALESCE(EXCLUDED.listing_date, stock_ipo.listing_date),
                    issue_price = COALESCE(EXCLUDED.issue_price, stock_ipo.issue_price),
                    lot_size = COALESCE(EXCLUDED.lot_size, stock_ipo.lot_size),
                    oversubscription_ratio = COALESCE(EXCLUDED.oversubscription_ratio, stock_ipo.oversubscription_ratio),
                    allotment_rate = COALESCE(EXCLUDED.allotment_rate, stock_ipo.allotment_rate)
            """, (ipo['stock_code'], ipo['stock_name'], ipo['listing_date'], ipo['issue_price'], ipo['lot_size'], ipo['oversubscription_ratio'], ipo['allotment_rate']))
            if cur.rowcount > 0:
                inserted += 1
        except Exception as e:
            print(f"插入失败 {ipo['stock_code']}: {e}")
    
    conn.commit()
    
    # 统计结果
    cur.execute("SELECT EXTRACT(YEAR FROM listing_date) as year, COUNT(*) FROM stock_ipo WHERE listing_date IS NOT NULL GROUP BY year ORDER BY year;")
    stats = cur.fetchall()
    
    cur.close()
    conn.close()
    
    print(f'\n成功处理 {inserted} 条记录')
    print('\n各年份数据统计:')
    for year, count in stats:
        print(f'  {int(year)}年: {count} 条')

if __name__ == '__main__':
    main()
