#!/usr/bin/env python3
"""从AASTOCKS爬取港股IPO详细数据"""
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
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
    'Referer': 'http://www.aastocks.com/',
}

conn = psycopg2.connect(host='localhost', port=5432, database='hk_stock', user='postgres', password='pc20050218')
cur = conn.cursor()

# 测试一个股票详情页
code = '00664'  # 铜师傅
url = f'http://www.aastocks.com/sc/stocks/market/ipo/upcomingipo/company-summary?symbol={code}#info'
resp = requests.get(url, headers=headers, timeout=15)
resp.encoding = 'utf-8'
soup = BeautifulSoup(resp.text, 'html.parser')

print(f'URL: {url}')
print(f'Status: {resp.status_code}')
print(f'Content length: {len(resp.text)}')

# 找所有表格
tables = soup.find_all('table')
print(f'\nTotal tables: {len(tables)}')

# 找IPO数据表格
for i, table in enumerate(tables):
    rows = table.find_all('tr')
    if len(rows) < 2:
        continue
    
    # 获取表头和首行数据
    header_row = rows[0]
    header_cells = [td.get_text(strip=True) for td in header_row.find_all(['td', 'th'])]
    data_row = rows[1] if len(rows) > 1 else None
    data_cells = [td.get_text(strip=True) for td in data_row.find_all(['td', 'th'])] if data_row else []
    
    full_text = ' '.join(header_cells) + ' '.join(data_cells)
    
    # 跳过导航和空表格
    if len([c for c in header_cells if c]) < 2:
        continue
    if any(x in full_text for x in ['首页', '登录', '版权']):
        continue
    
    print(f'\n=== Table {i} ({len(rows)} rows) ===')
    print(f'Header: {header_cells}')
    print(f'Data: {data_cells}')

# 找所有包含关键IPO字段的文本
print('\n=== 搜索关键字段 ===')
text = soup.get_text()
key_fields = ['认购', '超额', '中签', '基石', '保荐', '国际', '公开发售', '招股', '定价', '上市', '集资', '每手', '入场费', '市盈率', '行业']
for field in key_fields:
    count = text.count(field)
    if count > 0:
        # 找到包含该字段的上下文
        idx = text.find(field)
        context = text[max(0, idx-30):idx+50]
        print(f'{field}: 出现{count}次, 示例: "...{context}..."')