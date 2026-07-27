#!/usr/bin/env python3
"""Sync IPO details and tiered allotment rates from HKEX PDFs"""
import datetime as dt
import io
import json
import os
os.environ['NO_PROXY'] = '*'

import re
import sys
import time
import requests
import psycopg2
from bs4 import BeautifulSoup
from pypdf import PdfReader

requests.sessions.Session.trust_env = False
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "db"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "hk_stock"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "pc20050218"),
}

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/json,application/pdf',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Referer': 'http://www.aastocks.com/',
}

HKEX_HEADERS = {
    'User-Agent': HEADERS['User-Agent'],
    'Accept': 'application/json,text/html,application/xhtml+xml,application/pdf',
    'Accept-Language': 'en-US,en;q=0.9,zh-CN;q=0.8',
    'Referer': 'https://www1.hkexnews.hk/search/predefineddoc.xhtml?predefineddocuments=4&lang=en',
}


def parse_num(text):
    if not text:
        return None
    text = str(text).strip().replace(',', '').replace('%', '')
    if text in ('N/A', '-', '--', ''):
        return None
    match = re.search(r'-?\d+(?:\.\d+)?', text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except Exception:
        return None


def normalize_code(code):
    return str(code).strip().zfill(5)


def normalize_name(text):
    if not text:
        return ''
    text = str(text).upper()
    replacements = {
        '－': '-', '─': '-', '—': '-', '–': '-', '　': '', ' ': '',
        'Ｗ': 'W', 'Ｂ': 'B', 'Ｐ': 'P', 'Ａ': 'A', 'Ｈ': 'H',
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = re.sub(r'\(?\d+\.HK\)?', '', text)
    text = re.sub(r'[^0-9A-Z\u4e00-\u9fff-]', '', text)
    return text


def names_match(a, b):
    return normalize_name(a) == normalize_name(b)


def fetch_hkex_allotment_announcements(days=540):
    """Fetch HKEX allotment result announcements."""
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


def extract_allotment_rate_tiers(text):
    """Extract tiered allotment rates from HKEX PDF."""
    pool_match = re.search(r'POOL\s+A\s*(.*?)(?:Total\s+[\d,]+\s+Total number of Pool A|POOL\s+B)', text, re.I | re.S)
    if not pool_match:
        return {}

    pool_text = pool_match.group(1)
    row_matches = re.findall(
        r'(?m)^\s*([\d,]+)\s+([\d,]+)\s+(.{0,220}?)(\d+(?:\.\d+)?)%',
        pool_text,
    )
    if not row_matches:
        return {}

    applied_shares = []
    for shares_text, _applications, _basis, rate_text in row_matches:
        shares = parse_num(shares_text)
        rate = parse_num(rate_text)
        if shares is None or rate is None:
            continue
        applied_shares.append((int(shares), rate))

    if not applied_shares:
        return {}

    lot_size = min(shares for shares, _rate in applied_shares)
    if lot_size <= 0:
        return {}

    tiers = {}
    for shares, rate in applied_shares:
        if shares % lot_size != 0:
            continue
        lots = shares // lot_size
        tiers[str(lots)] = rate
    return tiers


def extract_hkex_allotment_pdf(pdf_url):
    """Extract data from HKEX allotment result PDF."""
    try:
        resp = requests.get(pdf_url, headers=HKEX_HEADERS, timeout=30)
        resp.raise_for_status()
        reader = PdfReader(io.BytesIO(resp.content))
        text = '\n'.join((page.extract_text() or '') for page in reader.pages)
    except Exception as exc:
        print(f'  HKEX PDF解析失败: {exc}')
        return {}

    data = {}
    subscription_match = re.search(r'Subscription\s+Level?\s*[:：]?\s*([\d,]+(?:\.\d+)?)\s+times', text, re.I)
    if subscription_match:
        data['oversubscription_ratio'] = parse_num(subscription_match.group(1))

    rate_tiers = extract_allotment_rate_tiers(text)
    if rate_tiers:
        ordered_tiers = dict(sorted(rate_tiers.items(), key=lambda item: int(item[0])))
        data['allotment_rate_tiers'] = json.dumps(ordered_tiers, ensure_ascii=False)
        data['allotment_rate'] = rate_tiers.get('1')

    if data.get('allotment_rate') is None:
        basis_match = re.search(
            r'POOL\s+A\s*\n\s*([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+out\s+of\s+([\d,]+)\s+applicants.*?([\d.]+)%',
            text, re.I | re.S,
        )
        if basis_match:
            data['allotment_rate'] = parse_num(basis_match.group(5))

    gross_match = re.search(r'Gross\s+proceeds.*?HK\$\s*([\d,]+(?:\.\d+)?)\s*(million|billion)?', text, re.I | re.S)
    if gross_match:
        amount = parse_num(gross_match.group(1))
        unit = (gross_match.group(2) or '').lower()
        if amount is not None:
            if unit == 'billion':
                amount *= 1_000_000_000
            elif unit == 'million':
                amount *= 1_000_000
            data['fundraising_amount'] = round(amount, 2)

    return data


def scrape_ipo_detail(stock_code, stock_name=None):
    """Scrape IPO details from AAStocks."""
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
                elif label.startswith('香港配售股份数目'):
                    share_count = parse_num(value)
                    ratio_match = re.search(r'\((\d+(?:\.\d+)?)%\)', value)
                    if ratio_match:
                        public_ratio = parse_num(ratio_match.group(1))
                        result['public_offering_ratio'] = public_ratio
                        if public_ratio is not None:
                            result['international_placement_ratio'] = round(100 - public_ratio, 4)
                    if share_count is not None:
                        result['public_offering_shares'] = share_count

        if '招股日期' in all_text and '定价日期' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all('td')]
                if len(cells) < 2:
                    continue
                label = cells[0].strip()
                value = cells[1].strip()
                if label == '行业' and value:
                    result['sector'] = value

        if '超额倍数' in all_text and '一手中签率' in all_text:
            for row in rows:
                cells = [td.get_text(strip=True) for td in row.find_all(['td', 'th'])]
                if len(cells) < 3 or cells[0] == '公司名称':
                    continue
                if stock_name and not names_match(stock_name, cells[0]):
                    continue
                result['oversubscription_ratio'] = parse_num(cells[1])
                result['allotment_rate'] = parse_num(cells[2])
                break

    if result.get('issue_price') is not None and result.get('public_offering_shares') is not None:
        result['fundraising_amount'] = round(result['issue_price'] * result['public_offering_shares'], 2)

    return result


def update_db(cur, code, data):
    """Update IPO data in database."""
    updates = []
    params = []
    mapping = {
        'issue_price': 'issue_price',
        'lot_size': 'lot_size',
        'entry_fee': 'entry_fee',
        'sponsor': 'sponsor',
        'sector': 'sector',
        'public_offering_ratio': 'public_offering_ratio',
        'international_placement_ratio': 'international_placement_ratio',
        'oversubscription_ratio': 'oversubscription_ratio',
        'allotment_rate': 'allotment_rate',
        'fundraising_amount': 'fundraising_amount',
        'allotment_rate_tiers': 'allotment_rate_tiers',
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


def ensure_schema(cur):
    """Ensure allotment_rate_tiers column exists."""
    cur.execute("""
        ALTER TABLE stock_ipo
        ADD COLUMN IF NOT EXISTS allotment_rate_tiers TEXT
    """)


def main():
    print("=" * 60)
    print("IPO 详情补全 - 包含阶梯中签率")
    print("=" * 60)
    
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    ensure_schema(cur)
    
    # Get all IPO stocks from 2025 onwards
    cur.execute("""
        SELECT stock_code, stock_name
        FROM stock_ipo
        WHERE listing_date >= '2025-01-01'
        ORDER BY listing_date DESC
    """)
    stocks = cur.fetchall()
    print(f'\n需要补全 IPO 详情的股票: {len(stocks)}')

    print('\n[1/3] 获取 HKEX 配发结果公告...')
    hkex_announcements = fetch_hkex_allotment_announcements()

    print('\n[2/3] 逐只补全详情...')
    updated = 0
    for index, (code, name) in enumerate(stocks, 1):
        print(f'\n  [{index}/{len(stocks)}] {code} {name}')
        data = scrape_ipo_detail(code, name)

        announcement = hkex_announcements.get(normalize_code(code))
        if announcement:
            print(f"    HKEX公告: {announcement['date_time']}")
            hkex_data = extract_hkex_allotment_pdf(announcement['file_link'])
            data.update({key: value for key, value in hkex_data.items() if value is not None})

        if data and update_db(cur, code, data):
            updated += 1
            tiers = json.loads(data.get('allotment_rate_tiers', '{}'))
            print(
                f"    -> 更新: 发行价={data.get('issue_price')}, 每手={data.get('lot_size')}, "
                f"中签率={data.get('allotment_rate')}%, 阶梯={len(tiers)}档"
            )
            if tiers:
                print(f"       阶梯详情: {tiers}")
        else:
            print('    -> 未获取到可更新详情')
        time.sleep(0.3)

    conn.commit()
    
    print(f'\n[3/3] 统计结果...')
    cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE allotment_rate_tiers IS NOT NULL")
    tiers_count = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM stock_ipo WHERE allotment_rate IS NOT NULL")
    rate_count = cur.fetchone()[0]
    
    print(f'\nIPO详情补全完成：')
    print(f'  更新: {updated}/{len(stocks)} 只')
    print(f'  有中签率: {rate_count} 只')
    print(f'  有阶梯中签率: {tiers_count} 只')

    cur.close()
    conn.close()
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
