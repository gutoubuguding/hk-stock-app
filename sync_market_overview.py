#!/usr/bin/env python3
"""同步大盘概览数据：恒生指数、恒生科技、国企指数 + 港股涨跌家数。"""
import os
os.environ['NO_PROXY'] = '*'

import sys
sys.stdout.reconfigure(encoding='utf-8', line_buffering=True)

import psycopg2
from datetime import datetime
import akshare as ak

# 数据库连接从环境变量读取，避免把本机密码提交到 GitHub。
DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "hk_stock"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}

INDEX_NAMES = {
    "HSI": "恒生指数",
    "HSTECH": "恒生科技指数",
    "HSCEI": "恒生中国企业指数",
}


def ensure_table(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS market_overview (
            id SERIAL PRIMARY KEY,
            index_code VARCHAR(20) NOT NULL,
            index_name VARCHAR(50),
            last_price DECIMAL(12, 2),
            change_val DECIMAL(12, 2),
            change_pct DECIMAL(8, 4),
            open_price DECIMAL(12, 2),
            high_price DECIMAL(12, 2),
            low_price DECIMAL(12, 2),
            prev_close DECIMAL(12, 2),
            volume BIGINT,
            turnover DECIMAL(20, 2),
            raise_count INT,
            fall_count INT,
            equal_count INT,
            update_time TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(index_code, update_time)
        )
    """)


def fetch_indices():
    """优先用新浪港股指数行情，字段更稳定；返回 HSI/HSTECH/HSCEI。"""
    df = ak.stock_hk_index_spot_sina()
    rows = []
    for code, name in INDEX_NAMES.items():
        match = df[df.iloc[:, 0].astype(str).str.upper() == code]
        if match.empty:
            continue
        row = match.iloc[0]
        last_price = float(row.iloc[2] or 0)
        change_val = float(row.iloc[3] or 0)
        change_pct = float(row.iloc[4] or 0)
        open_price = float(row.iloc[5] or 0)
        prev_close = last_price - change_val if last_price or change_val else 0
        rows.append({
            "code": code,
            "name": name,
            "last_price": round(last_price, 2),
            "change_val": round(change_val, 2),
            "change_pct": round(change_pct, 4),
            "open_price": round(open_price, 2),
            "high_price": round(float(row.iloc[7] or 0), 2),
            "low_price": round(float(row.iloc[8] or 0), 2),
            "prev_close": round(prev_close, 2),
            "volume": 0,
            "turnover": 0,
        })
    return rows


def calc_market_breadth(cur):
    """用本地最新两日K线计算全市场上涨/下跌/平盘家数，避免大盘页面长期为空。"""
    cur.execute("""
        WITH latest AS (
            SELECT stock_code, MAX(trade_date) AS trade_date
            FROM stock_kline
            WHERE period_type = 'D'
            GROUP BY stock_code
        ), current_day AS (
            SELECT k.stock_code, k.trade_date, k.close_price
            FROM stock_kline k
            JOIN latest l ON l.stock_code = k.stock_code AND l.trade_date = k.trade_date
            WHERE k.period_type = 'D' AND k.close_price IS NOT NULL
        ), previous_day AS (
            SELECT DISTINCT ON (k.stock_code) k.stock_code, k.close_price
            FROM stock_kline k
            JOIN current_day c ON c.stock_code = k.stock_code
            WHERE k.period_type = 'D'
              AND k.trade_date < c.trade_date
              AND k.close_price IS NOT NULL
            ORDER BY k.stock_code, k.trade_date DESC
        )
        SELECT
            COUNT(*) FILTER (WHERE c.close_price > p.close_price) AS raise_count,
            COUNT(*) FILTER (WHERE c.close_price < p.close_price) AS fall_count,
            COUNT(*) FILTER (WHERE c.close_price = p.close_price) AS equal_count
        FROM current_day c
        JOIN previous_day p ON p.stock_code = c.stock_code
    """)
    row = cur.fetchone() or (0, 0, 0)
    return int(row[0] or 0), int(row[1] or 0), int(row[2] or 0)


def save_to_db(indices, breadth):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    ensure_table(cur)
    raise_count, fall_count, equal_count = breadth or calc_market_breadth(cur)
    update_time = datetime.now().replace(microsecond=0)

    for idx in indices:
        cur.execute("""
            INSERT INTO market_overview (
                index_code, index_name, last_price, change_val, change_pct,
                open_price, high_price, low_price, prev_close, volume, turnover,
                raise_count, fall_count, equal_count, update_time, created_at
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
            ON CONFLICT (index_code, update_time) DO UPDATE SET
                index_name = EXCLUDED.index_name,
                last_price = EXCLUDED.last_price,
                change_val = EXCLUDED.change_val,
                change_pct = EXCLUDED.change_pct,
                open_price = EXCLUDED.open_price,
                high_price = EXCLUDED.high_price,
                low_price = EXCLUDED.low_price,
                prev_close = EXCLUDED.prev_close,
                volume = EXCLUDED.volume,
                turnover = EXCLUDED.turnover,
                raise_count = EXCLUDED.raise_count,
                fall_count = EXCLUDED.fall_count,
                equal_count = EXCLUDED.equal_count
        """, (
            idx["code"], idx["name"], idx["last_price"], idx["change_val"], idx["change_pct"],
            idx["open_price"], idx["high_price"], idx["low_price"], idx["prev_close"],
            idx["volume"], idx["turnover"], raise_count, fall_count, equal_count, update_time
        ))

    conn.commit()
    cur.close()
    conn.close()


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()
    ensure_table(cur)
    breadth = calc_market_breadth(cur)
    conn.commit()
    cur.close()
    conn.close()

    indices = fetch_indices()
    if not indices:
        raise RuntimeError("未获取到指数行情")

    save_to_db(indices, breadth)
    print(f"保存大盘概览 {len(indices)} 条，涨跌家数：涨 {breadth[0]} / 跌 {breadth[1]} / 平 {breadth[2]}")
    for idx in indices:
        print(f"{idx['code']} {idx['name']}: {idx['last_price']} {idx['change_val']} ({idx['change_pct']}%)")


if __name__ == '__main__':
    main()
