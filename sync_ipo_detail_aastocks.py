#!/usr/bin/env python3
"""从 AASTOCKS 补全 IPO 发行价、每手股数、入场费、保荐人等详情。

Futu IPO 列表有时只给入场费/上市日期，不给发行价；近一年新股对比的
首日/7日/30日/现价涨跌都依赖发行价，所以指标同步前先跑一次详情补全。
"""
import datetime as dt
import io
import os
os.environ['NO_PROXY'] = '*'

import re
import sys
import time
import requests
import psycopg2
from bs4 import BeautifulSoup
try:
    from pypdf import PdfReader
except Exception:  # pypdf is installed in the backend image via requirements-sync.txt
    PdfReader = None

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
    # AASTOCKS 有时给区间，例如 “10.00-12.00”，表格展示单一发行价时取第一个数字。
    match = re.search(r'-?\d+(?:\.\d+)?', text)
    if not match:
        return None
    try:
        return float(match.group(0))
    except Exception:
        return None


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


def names_match(left, right):
    left_norm = normalize_name(left)
    right_norm = normalize_name(right)
    return bool(left_norm and right_norm and (left_norm in right_norm or right_norm in left_norm))


def normalize_code(stock_code):
    return str(stock_code or '').strip().replace('.HK', '').zfill(5)


def fetch_hkex_allotment_announcements(days=370):
    """批量读取 HKEXnews Title Search 的 Allotment Results。

    AASTOCKS 详情页的小表只给“最近几只”的中签率/超购倍数；HKEXnews 的
    Allotment Results 公告才是正式批量来源。按月切片查询，避免结果超过页面
    单次最多展示 100 条后被截断。
    """
    session = requests.Session()
    session.trust_env = False
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
            # Title Search 的 Allotment Results 分类会混入供股、配售、债券等非 IPO 公告。
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


def extract_hkex_allotment_pdf(pdf_url):
    if PdfReader is None:
        return {}
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

    basis_match = re.search(
        r'POOL\s+A\s*\n\s*([\d,]+)\s+([\d,]+)\s+([\d,]+)\s+out\s+of\s+([\d,]+)\s+applicants.*?([\d.]+)%',
        text,
        re.I | re.S,
    )
    if basis_match:
        data['allotment_rate'] = parse_num(basis_match.group(5))
    else:
        # 兼容少数 PDF 抽文本换行不同的情况：取 BASIS OF ALLOCATION 后第一条百分比。
        section_match = re.search(r'BASIS\s+OF\s+ALLOCATION\s+UNDER\s+THE\s+HONG\s+KONG\s+PUBLIC\s+OFFERING(.{0,4000})', text, re.I | re.S)
        if section_match:
            percent_match = re.search(r'(\d+(?:\.\d+)?)%', section_match.group(1))
            if percent_match:
                data['allotment_rate'] = parse_num(percent_match.group(1))

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
          AND (
              issue_price IS NULL OR lot_size IS NULL OR sponsor IS NULL OR sector IS NULL
              OR public_offering_ratio IS NULL OR international_placement_ratio IS NULL
              OR oversubscription_ratio IS NULL OR allotment_rate IS NULL OR fundraising_amount IS NULL
          )
        ORDER BY listing_date DESC
    """)
    stocks = cur.fetchall()
    print(f'需要补全 IPO 详情的股票: {len(stocks)}')

    hkex_announcements = fetch_hkex_allotment_announcements()

    updated = 0
    for index, (code, name) in enumerate(stocks, 1):
        print(f'[{index}/{len(stocks)}] {code} {name}')
        data = scrape_ipo_detail(code, name)

        announcement = hkex_announcements.get(normalize_code(code))
        if announcement:
            print(f"  HKEX公告: {announcement['date_time']} {announcement['title']}")
            hkex_data = extract_hkex_allotment_pdf(announcement['file_link'])
            # HKEX正式公告优先覆盖 AASTOCKS 小表结果。
            data.update({key: value for key, value in hkex_data.items() if value is not None})

        if data and update_db(cur, code, data):
            updated += 1
            print(
                f"  -> 更新: 发行价={data.get('issue_price')}, 每手={data.get('lot_size')}, "
                f"公开发售={data.get('public_offering_ratio')}, 国际配售={data.get('international_placement_ratio')}, "
                f"超购={data.get('oversubscription_ratio')}, 中签率={data.get('allotment_rate')}"
            )
        else:
            print('  -> 未获取到可更新详情')
        time.sleep(0.3)

    conn.commit()
    cur.close()
    conn.close()
    print(f'IPO详情补全完成：更新 {updated}/{len(stocks)} 只')


if __name__ == '__main__':
    main()
