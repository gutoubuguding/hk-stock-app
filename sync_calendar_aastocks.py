# -*- coding: utf-8 -*-
"""
同步港股财报/分红日历。
数据源: AASTOCKS Corporate Events
- Result Announcements: http://www.aastocks.com/EN/stocks/market/calendar.aspx
- Company Dividend: http://www.aastocks.com/EN/stocks/market/calendar.aspx?type=5

写入 stock_calendar：
- FINANCIAL: event_date = 结果公布日期
- DIVIDEND: event_date = 除净日（如无除净日则用派息日/公告日）
"""

import html
import os
import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

import psycopg2
import requests
from bs4 import BeautifulSoup

# 数据库连接从环境变量读取，避免把本机密码提交到 GitHub。
DB_CONFIG = dict(
    host=os.getenv("DB_HOST", "localhost"),
    port=int(os.getenv("DB_PORT", "5432")),
    dbname=os.getenv("DB_NAME", "hk_stock"),
    user=os.getenv("DB_USER", "postgres"),
    password=os.getenv("DB_PASSWORD", ""),
)
BASE = "http://www.aastocks.com/EN/stocks/market/calendar.aspx"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/122 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9,zh-CN;q=0.8",
}


def fetch(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=25)
    resp.raise_for_status()
    return resp.text


def clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", html.unescape(value or "")).strip()


def parse_date(value: str):
    value = clean_text(value)
    if not value or value.upper() == "N/A":
        return None
    m = re.search(r"(20\d{2})[/-](\d{1,2})[/-](\d{1,2})", value)
    if not m:
        return None
    return date(int(m.group(1)), int(m.group(2)), int(m.group(3)))


def parse_amount(value: str):
    # Examples: D:HKD 0.0060, D:USD 0.0600 (Ordinary Cash Dividend)
    m = re.search(r"D:\s*([A-Z]{3})\s*([0-9.]+)", value or "", re.I)
    if not m:
        return None
    try:
        return Decimal(m.group(2))
    except InvalidOperation:
        return None


def split_name_code(cell):
    link = cell.find("a", href=re.compile(r"symbol=\d+"))
    if not link:
        return None, None
    code = clean_text(link.get_text()).replace(".HK", "")
    text = cell.get_text(" ", strip=True)
    text = re.sub(r"\b\d{5}\.HK\b", "", text).strip()
    return code, clean_text(text)


def parse_financial_rows(text: str):
    soup = BeautifulSoup(text, "html.parser")
    rows = []
    current_date = None
    for tr in soup.select("tr.crtRow"):
        cells = tr.find_all("td")
        if len(cells) < 4:
            continue
        first = clean_text(cells[0].get_text(" ", strip=True))
        dt = parse_date(first)
        if dt:
            current_date = dt
        if not current_date:
            continue
        code, name = split_name_code(cells[1])
        if not code:
            continue
        report_type = clean_text(cells[-1].get_text(" ", strip=True))
        rows.append({
            "stock_code": code,
            "stock_name": name,
            "event_type": "FINANCIAL",
            "event_date": current_date,
            "dividend_per_share": None,
            "ex_dividend_date": None,
            "payment_date": None,
            "financial_report_type": report_type,
        })
    return rows


def parse_dividend_rows(text: str):
    soup = BeautifulSoup(text, "html.parser")
    rows = []
    current_announce_date = None
    for tr in soup.select("tr.crtRow"):
        cells = tr.find_all("td")
        if len(cells) < 4:
            continue
        first = clean_text(cells[0].get_text(" ", strip=True))
        dt = parse_date(first)
        if dt:
            current_announce_date = dt
        code, name = split_name_code(cells[1])
        if not code:
            continue
        dividend_text = clean_text(cells[2].get_text(" ", strip=True))
        date_text = cells[3].get_text("\n", strip=True)
        ex_date = parse_date(re.search(r"Ex-Date:\s*([^\n]+)", date_text).group(1) if re.search(r"Ex-Date:\s*([^\n]+)", date_text) else "")
        pay_date = parse_date(re.search(r"Payable:\s*([^\n]+)", date_text).group(1) if re.search(r"Payable:\s*([^\n]+)", date_text) else "")
        event_date = ex_date or pay_date or current_announce_date
        if not event_date:
            continue
        rows.append({
            "stock_code": code,
            "stock_name": name,
            "event_type": "DIVIDEND",
            "event_date": event_date,
            "dividend_per_share": parse_amount(dividend_text),
            "ex_dividend_date": ex_date,
            "payment_date": pay_date,
            "financial_report_type": dividend_text,
        })
    return rows


def upsert_rows(rows):
    if not rows:
        return 0
    sql = """
    INSERT INTO stock_calendar (
        stock_code, stock_name, event_type, event_date,
        dividend_per_share, ex_dividend_date, payment_date, financial_report_type, created_at
    ) VALUES (%(stock_code)s, %(stock_name)s, %(event_type)s, %(event_date)s,
        %(dividend_per_share)s, %(ex_dividend_date)s, %(payment_date)s, %(financial_report_type)s, NOW())
    ON CONFLICT (stock_code, event_type, event_date) DO UPDATE SET
        stock_name = EXCLUDED.stock_name,
        dividend_per_share = EXCLUDED.dividend_per_share,
        ex_dividend_date = EXCLUDED.ex_dividend_date,
        payment_date = EXCLUDED.payment_date,
        financial_report_type = EXCLUDED.financial_report_type,
        created_at = NOW()
    """
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            ensure_unique_sql = """
            DO $$
            BEGIN
              IF NOT EXISTS (
                SELECT 1 FROM pg_indexes WHERE schemaname = 'public' AND indexname = 'uk_stock_calendar_event'
              ) THEN
                CREATE UNIQUE INDEX uk_stock_calendar_event ON stock_calendar(stock_code, event_type, event_date);
              END IF;
            END $$;
            """
            cur.execute("ALTER TABLE stock_calendar ALTER COLUMN financial_report_type TYPE VARCHAR(255)")
            cur.execute(ensure_unique_sql)
            cur.executemany(sql, rows)
        conn.commit()
    return len(rows)


def prune_old(days=120):
    cutoff = date.today() - timedelta(days=days)
    with psycopg2.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM stock_calendar WHERE event_date < %s", (cutoff,))
            deleted = cur.rowcount
        conn.commit()
    return deleted


def main():
    financial = parse_financial_rows(fetch(BASE))
    dividend = parse_dividend_rows(fetch(BASE + "?type=5"))
    # 保留当前及未来附近的数据，避免页面被过多历史分红淹没。
    today = date.today()
    future_limit = today + timedelta(days=180)
    rows = [r for r in financial + dividend if today - timedelta(days=30) <= r["event_date"] <= future_limit]
    count = upsert_rows(rows)
    deleted = prune_old()
    print(f"calendar synced: parsed financial={len(financial)}, dividend={len(dividend)}, upserted={count}, pruned={deleted}")


if __name__ == "__main__":
    main()
