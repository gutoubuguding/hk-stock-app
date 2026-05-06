#!/usr/bin/env python3
"""根据已同步的日K线自动回填 IPO 首日、7日、30日涨跌幅。"""
import os
import psycopg2
from decimal import Decimal, ROUND_HALF_UP

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "hk_stock"),
    "user": os.getenv("DB_USER", "postgres"),
    "password": os.getenv("DB_PASSWORD", "")
}


def pct(close_price, issue_price):
    if close_price is None or issue_price is None or issue_price == 0:
        return None
    value = (Decimal(close_price) - Decimal(issue_price)) / Decimal(issue_price) * Decimal(100)
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def main():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    cur.execute("""
        SELECT stock_code, stock_name, issue_price, listing_date,
               first_day_change, seven_day_change, thirty_day_change
        FROM stock_ipo
        WHERE listing_date IS NOT NULL
          AND issue_price IS NOT NULL
          AND issue_price > 0
          AND listing_date <= CURRENT_DATE
        ORDER BY listing_date DESC
    """)
    ipos = cur.fetchall()

    updated = 0
    filled_1d = filled_7d = filled_30d = 0
    waiting_7d = waiting_30d = 0

    for code, name, issue_price, listing_date, old_1d, old_7d, old_30d in ipos:
        cur.execute("""
            SELECT trade_date, close_price
            FROM stock_kline
            WHERE stock_code = %s
              AND period_type = 'D'
              AND trade_date >= %s
              AND close_price IS NOT NULL
            ORDER BY trade_date ASC
            LIMIT 35
        """, (code, listing_date))
        rows = cur.fetchall()
        if not rows:
            continue

        new_1d = old_1d
        new_7d = old_7d
        new_30d = old_30d

        if old_1d is None and len(rows) >= 1:
            new_1d = pct(rows[0][1], issue_price)
            if new_1d is not None:
                filled_1d += 1

        # 第7/30个交易日收盘价：上市首个交易日为第1个交易日，所以索引分别为 6 / 29
        if old_7d is None:
            if len(rows) >= 7:
                new_7d = pct(rows[6][1], issue_price)
                if new_7d is not None:
                    filled_7d += 1
            else:
                waiting_7d += 1

        if old_30d is None:
            if len(rows) >= 30:
                new_30d = pct(rows[29][1], issue_price)
                if new_30d is not None:
                    filled_30d += 1
            else:
                waiting_30d += 1

        if new_1d != old_1d or new_7d != old_7d or new_30d != old_30d:
            cur.execute("""
                UPDATE stock_ipo
                SET first_day_change = %s,
                    seven_day_change = %s,
                    thirty_day_change = %s,
                    updated_at = NOW()
                WHERE stock_code = %s
            """, (new_1d, new_7d, new_30d, code))
            updated += 1
            print(f"{code} {name}: 首日={new_1d}, 7日={new_7d}, 30日={new_30d} (K线{len(rows)}条)")

    conn.commit()
    cur.close()
    conn.close()

    print(f"完成：更新 {updated} 只；补首日 {filled_1d}，补7日 {filled_7d}，补30日 {filled_30d}；等待7日 {waiting_7d}，等待30日 {waiting_30d}")


if __name__ == '__main__':
    main()
