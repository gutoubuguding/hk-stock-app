#!/usr/bin/env python3
"""Update IPO records with HKEX PDF URLs"""
import sys
sys.stdout.reconfigure(encoding='utf-8')
import os
os.environ['NO_PROXY'] = '*'
import re
import requests
import psycopg2
from bs4 import BeautifulSoup
import time

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "hk_stock"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "pc20050218"),
}

HKEX_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json,text/html,application/xhtml+xml,application/pdf',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8',
    'Referer': 'https://www1.hkexnews.hk/search/predefineddoc.xhtml?predefineddocuments=4&lang=en',
}

def normalize_code(code):
    return str(code).strip().zfill(5)

def fetch_hkex_allotment_announcements(days=540):
    """Fetch HKEX allotment result announcements with PDF URLs."""
    import datetime as dt
    session = requests.Session()
    session.headers.update(HKEX_HEADERS)
    start = dt.date.today() - dt.timedelta(days=days)
    end = dt.date.today()
    announcements = {}

    try:
        initial = session.get('https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en', timeout=20)
        initial.raise_for_status()
        form_id_match = re.search(r'<form id="([^"]+)"', initial.text)
        view_state_match = re.search(r'name="javax.faces.ViewState"[^>]+value="([^"]+)"', initial.text)
        if not form_id_match or not view_state_match:
            raise RuntimeError('无法识别HKEX Title Search表单')
        form_id = form_id_match.group(1)
        view_state = view_state_match.group(1)
    except Exception as exc:
        print(f'HKEX配发结果列表获取失败: {exc}')
        return {}

    cursor = start
    while cursor <= end:
        chunk_end = min(cursor + dt.timedelta(days=31), end)
        data = {
            form_id: form_id,
            f'{form_id}:loadMoreRange': '100',
            'javax.faces.ViewState': view_state,
            'titleSearchResultControl.searchByIndex': '0',
            'titleSearchByAllResult.dateFromUi': '',
            'titleSearchByAllResult.dateToUi': '',
            'lang': 'EN',
            'category': '0',
            'market': 'SEHK',
            'searchType': '1',
            'documentType': '-2',
            't1code': '10000',
            't2Gcode': '5',
            't2code': '15100',
            'stockId': '',
            'from': cursor.strftime('%Y%m%d'),
            'to': chunk_end.strftime('%Y%m%d'),
            'title': '',
        }
        try:
            resp = session.post(
                'https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en',
                data=data,
                timeout=30,
            )
            resp.raise_for_status()
        except Exception as exc:
            print(f'  HKEX {cursor}~{chunk_end} 查询失败: {exc}')
            cursor = chunk_end + dt.timedelta(days=1)
            continue

        soup = BeautifulSoup(resp.text, 'html.parser')
        for row in soup.select('table tbody tr'):
            cells = [td.get_text(' ', strip=True) for td in row.find_all('td')]
            links = [a.get('href') for a in row.find_all('a') if a.get('href')]
            if len(cells) < 4 or not links:
                continue
            code_match = re.search(r'(\d{4,5})', cells[1])
            if not code_match:
                continue
            title = cells[3]
            title_upper = title.upper()
            if 'RIGHTS ISSUE' in title_upper or 'PLACING' in title_upper or 'BONDS' in title_upper:
                continue
            if 'ALLOTMENT RESULTS' not in title_upper:
                continue
            file_link = links[-1]
            code = normalize_code(code_match.group(1))
            announcements[code] = {
                'title': re.sub(r'\s+', ' ', title),
                'file_link': file_link if file_link.startswith('http') else f'https://www1.hkexnews.hk{file_link}',
                'date_time': cells[0].replace('Release Time:', '').strip(),
            }
        cursor = chunk_end + dt.timedelta(days=1)
        time.sleep(0.1)

    print(f'HKEX配发结果公告匹配池: {len(announcements)} 条')
    return announcements


def main():
    print("=" * 60)
    print("更新 IPO HKEX PDF 链接")
    print("=" * 60)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    
    # Get all IPO stocks
    cur.execute("""
        SELECT stock_code, stock_name
        FROM stock_ipo
        WHERE listing_date >= '2025-01-01'
        ORDER BY listing_date DESC
    """)
    stocks = cur.fetchall()
    print(f'\n找到 {len(stocks)} 只新股')
    
    print('\n获取 HKEX 配发结果公告...')
    announcements = fetch_hkex_allotment_announcements()
    
    updated = 0
    for code, name in stocks:
        normalized = normalize_code(code)
        if normalized in announcements:
            pdf_url = announcements[normalized]['file_link']
            cur.execute("""
                UPDATE stock_ipo 
                SET hkex_pdf_url = %s 
                WHERE stock_code = %s AND hkex_pdf_url IS NULL
            """, (pdf_url, code))
            if cur.rowcount > 0:
                updated += 1
                print(f'  {code} {name}: {pdf_url[:60]}...')
    
    conn.commit()
    cur.close()
    conn.close()
    
    print(f'\n完成！更新 {updated} 条 PDF 链接')
    print("=" * 60)


if __name__ == '__main__':
    main()
