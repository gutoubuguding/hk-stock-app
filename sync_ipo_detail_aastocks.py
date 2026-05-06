#!/usr/bin/env python3
"""从 AASTOCKS 补全 IPO 发行价、每手股数、入场费、保荐人等详情。

Futu IPO 列表有时只给入场费/上市日期，不给发行价；近一年新股对比的
首日/7日/30日/现价涨跌都依赖发行价，所以指标同步前先跑一次详情补全。
"""
import os
os.environ['NO_PROXY'] = '*'

import re
import sys
import time
import requests
import psycopg2
from bs4 import BeautifulSoup

requests.sessions.Session.trust_env = False
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "hk_stock"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", ""),
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'http://www.aastocks.com/',
}


def parse_num(text):
    if not text:
        return None
    text = str(text).strip().replace(',', '').replace('%', '')
    if text in ('N/A', '-', '--', ''):
        return None
    # AASTOCKS 有时给区间，例如 “10.00-12.00”，表格展示单一发行价时取第一个数字。
    match = re.search(r'-?\d+(?:\.\d+)?', text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except Exception:
        return None


def scrape_ipo_detail(stock_code):
    url = f'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol={stock_code}#info'
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.encoding = 'utf-8'
    except Exception as exc:
        print(f'  AASTOCKS请求失败: {exc}')
        return {}

    soup = BeautifulSoup(resp.text, 'html.parser')
    result = {}

    for table in soup.find_all('table'):
        rows = table.find_all('tr')
        all_text = ' '.join(td.get_text(strip=True) for td in table.find_all('td'))

        if '每手股数' in all_text and '招股价' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) < 2:
                    continue
                label = cells[0].strip()
                value = cells[1].strip()
                if label == '招股价':
                    result['issue_price'] = parse_num(value)
                elif label == '每手股数':
                    result['lot_size'] = parse_num(value)
                elif label == '入场费':
                    result['entry_fee'] = parse_num(value)
                elif label == '保荐人' and value:
                    result['sponsor'] = value
                elif label == '香港配售股份数目':
                    match = re.search(r'\((\d+(?:\.\d+)?)%\)', value)
                    if match:
                        result['public_offering_ratio'] = parse_num(match.group(1))

        if '招股日期' in all_text and '定价日期' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) < 2:
                    continue
                label = cells[0].strip()
                value = cells[1].strip()
                if label == '行业' and value:
                    result['sector'] = value

    return result


def update_db(cur, code, data):
    updates = []
    params = []
    mapping = {
        'issue_price': 'issue_price',
        'lot_size': 'lot_size',
        'entry_fee': 'entry_fee',
        'sponsor': 'sponsor',
        'sector': 'sector',
        'public_offering_ratio': 'public_offering_ratio',
    }
    for src, dst in mapping.items():
        value = data.get(src)
        if value is not None:
            updates.append(f'{dst} = COALESCE(%s, {dst})')
            params.append(value)

    if not updates:
        return False

    params.append(code)
    cur.execute(f"""
        UPDATE stock_ipo
        SET {', '.join(updates)}, updated_at = NOW()
        WHERE stock_code = %s
    """, params)
    return cur.rowcount > 0


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    cur.execute("""
        SELECT stock_code, stock_name
        FROM stock_ipo
        WHERE listing_date >= CURRENT_DATE - INTERVAL '1 year'
          AND (issue_price IS NULL OR lot_size IS NULL OR sponsor IS NULL OR sector IS NULL)
        ORDER BY listing_date DESC
    """)
    stocks = cur.fetchall()
    print(f'需要补全 IPO 详情的股票: {len(stocks)}')

    updated = 0
    for index, (code, name) in enumerate(stocks, 1):
        print(f'[{index}/{len(stocks)}] {code} {name}')
        data = scrape_ipo_detail(code)
        if data and update_db(cur, code, data):
            updated += 1
            print(f"  -> 更新: 发行价={data.get('issue_price')}, 每手={data.get('lot_size')}, 入场费={data.get('entry_fee')}")
        else:
            print('  -> 未获取到可更新详情')
        time.sleep(0.3)

    conn.commit()
    cur.close()
    conn.close()
    print(f'IPO详情补全完成：更新 {updated}/{len(stocks)} 只')


if __name__ == '__main__':
    main()
