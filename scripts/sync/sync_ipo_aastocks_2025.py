#!/usr/bin/env python3
"""从AAStocks同步2025年港股IPO数据"""
import sys
import os
os.environ['NO_PROXY'] = '*'

sys.stdout.reconfigure(encoding='utf-8')
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import psycopg2

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
    """解析日期字符串"""
    if not text or text.strip() == '-':
        return None
    text = text.strip()
    for fmt in ['%Y/%m/%d', '%Y-%m-%d', '%d/%m/%Y', '%m/%d/%Y']:
        try:
            return datetime.strptime(text, fmt).date()
        except:
            continue
    return None

def main():
    print("从AAStocks同步2025年港股IPO数据...")
    
    # AAStocks IPO页面
    url = "http://www.aastocks.com/sc/stocks/market/ipo/listedipo.aspx"
    
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.encoding = 'utf-8'
    except Exception as e:
        print(f"请求失败: {e}")
        return
    
    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # 查找IPO表格
    tables = soup.find_all('table')
    ipo_data = []
    
    for table in tables:
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            if len(cells) >= 4:
                # 尝试解析股票代码、名称、上市日期
                code_cell = cells[0].get_text(strip=True)
                name_cell = cells[1].get_text(strip=True)
                date_cell = cells[2].get_text(strip=True) if len(cells) > 2 else ''
                
                # 检查是否是股票代码格式（5位数字）
                if code_cell and code_cell.isdigit() and len(code_cell) == 5:
                    listing_date = parse_date(date_cell)
                    if listing_date and listing_date.year == 2025:
                        ipo_data.append({
                            'stock_code': code_cell,
                            'stock_name': name_cell,
                            'listing_date': listing_date,
                            'status': 'listed'
                        })
    
    print(f"从AAStocks获取到 {len(ipo_data)} 条2025年IPO记录")
    
    if not ipo_data:
        print("未找到2025年IPO数据")
        return
    
    # 插入数据库
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    inserted = 0
    for ipo in ipo_data:
        try:
            cur.execute("""
                INSERT INTO stock_ipo (stock_code, stock_name, listing_date, status)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (stock_code) DO UPDATE SET
                    stock_name = EXCLUDED.stock_name,
                    listing_date = EXCLUDED.listing_date,
                    status = EXCLUDED.status
            """, (ipo['stock_code'], ipo['stock_name'], ipo['listing_date'], ipo['status']))
            inserted += cur.rowcount
        except Exception as e:
            print(f"插入失败 {ipo['stock_code']}: {e}")
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f"成功插入/更新 {inserted} 条2025年IPO记录")

if __name__ == '__main__':
    main()
